from tensorhive.core.utils.decorators.override import override
from tensorhive.models.User import User
from typing import Generator, Dict, List
from tensorhive.config import EMAIL_BOT
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
        self.mailer = Mailer(server=EMAIL_BOT.SMTP_SERVER, port=EMAIL_BOT.SMTP_PORT)

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
                    log.debug('Delaying email Next attempt in {}'.format(self.interval - (timenow - timer)))
                    # That session is not ready to be penalized
                    pass
            else:
                # We should penalize any new unauthorized session
                time_left[username] = timenow
                result.append(session)
        # self.time_between_notifications = time_left
        return result

    @override
    def trigger_action(self, connection, unauthorized_sessions):
        sessions = self.filter_sessions(unauthorized_sessions)

        if not sessions:
            # There's no need to go further if we have no sessions 
            # to penalize (they must wait until timer resets)
            return

        self.mailer.connect(login=EMAIL_BOT.SMTP_LOGIN, password=os.getenv(EMAIL_BOT.SMTP_PASSWORD_ENV))
        for session in sessions:
            recipients = []
            try:
                # Fetch user
                username = session['USER']
                user = User.find_by_username(username)
                recipients.append(user.email)
            except Exception as e:
                log.error('Intruder does not have an account!')
                log.error(e)
            
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
