from tensorhive.core.utils.decorators.override import override
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.models.User import User
from typing import Generator, Dict, List, Any
from tensorhive.config import MAILBOT
from tensorhive.core.utils.mailer import Mailer, Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from inspect import cleandoc
import datetime
import smtplib
import os
import logging
log = logging.getLogger(__name__)


class EmailSendingBehaviour:
    message = cleandoc('''
                You are violating {legitimate_owner_username}\'s reservation!
                Please, stop all your computations on {gpu_uuid}.
                ''')

    def __init__(self):
        self.interval = datetime.timedelta(minutes=1)
        self.time_between_notifications = {}
        self.mailer = Mailer(server=MAILBOT.SMTP_SERVER, port=MAILBOT.SMTP_PORT)

    def filter_sessions(self, sessions):
        result = []
        time_left = self.time_between_notifications

        for session in sessions:
            # Fetch how much time left for specific user
            username = session['USER']
            timer = time_left.get(username)

            # Check if time is out
            timenow = datetime.datetime.utcnow()
            if timer:
                if timer + self.interval <= timenow:
                    # We should penalize that session
                    result.append(session)
                    del time_left[username]
                else:
                    #FIXME Remove this later
                    log.debug('Email warning postponed, next attempt in {}'.format(self.interval - (timenow - timer)))
                    # That session is not ready to be penalized
                    pass
            else:
                # We should penalize any new unauthorized session
                time_left[username] = timenow
                result.append(session)
        # self.time_between_notifications = time_left
        return result

    def prepare_message(self, session: Dict[str, Any], recipients: List[str]) -> Message:
        email_body = self.message.format(
            legitimate_owner_username=session['LEGITIMATE_USER'],
            gpu_uuid=session['GPU_UUID']
        )
        return Message(
            author=os.getenv(MAILBOT.SMTP_LOGIN_ENV),
            to=recipients,
            subject='Reservation has been violated',
            body=email_body
        )

    @override
    def trigger_action(self, connection, unauthorized_sessions):
        sessions = self.filter_sessions(unauthorized_sessions)

        # There's no need to go further if we have no sessions
        # to penalize (they must wait until timer resets)
        if not sessions:
            return

        self.mailer.connect(
            login=os.getenv(MAILBOT.SMTP_LOGIN_ENV),
            password=os.getenv(MAILBOT.SMTP_PASSWORD_ENV)
        )

        for session in sessions:
            recipients = []

            # Try to fetch intruder's account
            try:
                username = session['USER']
                user = User.find_by_username(username)
                recipients.append(user.email)
            except NoResultFound as e:
                log.error('Cannot send email to {}, reason: no account!'.format(username))
            except Exception as e:
                log.critical(e)

            # Admin should always get a notification
            # Even when intruder does not have an account
            if EMAIL_BOT.NOTIFY_ADMIN:
                recipients.append(EMAIL_BOT.ADMIN_EMAIL)    

            # Send message only if intruder has an account
            # and admin enabled self-notifications
            if recipients:
                # Prepare email and send
                email_body = self.message.format(
                    legitimate_owner_username=session['LEGITIMATE_USER'],
                    gpu_uuid=session['GPU_UUID']
                )
                email = Message(author=EMAIL_BOT.SMTP_LOGIN, to=recipients, subject=EMAIL_BOT.SUBJECT, body=email_body)
                self.mailer.send(email)
                log.debug('Email sent to: {}'.format(email.recipients))
        self.mailer.disconnect()
