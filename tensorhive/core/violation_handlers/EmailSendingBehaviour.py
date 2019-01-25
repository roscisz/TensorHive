from tensorhive.core.utils.decorators.override import override
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.models.User import User
from typing import Generator, Dict, List, Any, Optional
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
        self.time_of_last_email = {}
        self.mailer = Mailer(server=MAILBOT.SMTP_SERVER, port=MAILBOT.SMTP_PORT)

    def filter_sessions(self, violation_data):
        result = []
        # self.time_between_notifications = time_left
        return result

    def prepare_message(self, violation_data: Dict[str, Any], recipients: List[str]) -> Message:
        try:
            email_body = MAILBOT.INTRUDER_BODY_TEMPLATE.format(
                hostname=violation_data['HOSTNAME'],
                gpu_name='TODO',
                gpu_uuid=violation_data['UUID'],
                reservation_owner=violation_data['RESERVATION_OWNER'],
                reservation_end=violation_data['RESERVATION_END'],
            )
        except (KeyError, Exception) as e:
            log.error(e)
            # Put raw, unformatted body text
            email_body = MAILBOT.INTRUDER_BODY_TEMPLATE
        finally:
            return Message(
                author=os.getenv(MAILBOT.SMTP_LOGIN_ENV),
                to=recipients,
                subject=MAILBOT.INTRUDER_SUBJECT,
                body=email_body
            )

    def fetch_email_address(self, username: str) -> Optional[str]:
        email = None
        try:
            intruder = User.find_by_username(username)
        except NoResultFound as e:
            log.error('Cannot find email address for {}, reason: no account!'.format(username))
        except Exception as e:
            log.critical(e)
        else:
            email = intruder.email
        finally:
            return email

    def ready_to_send(self, email_address: str) -> bool:
        '''
        Allows for sending email only once every given time
        to a particular email address
        '''
        try:
            ready_status = self.time_of_last_email[email_address] + self.interval < datetime.datetime.utcnow()
        except KeyError as e:
            ready_status = True
        finally:
            return ready_status

    @override
    def trigger_action(self, violation_data: Dict[str, Any]):
        # TODO FRIDAY: Admin and intruder get different messages
        try:
            # Expect proper keys beforehand
            assert set(['INTRUDER', 'RESERVATION_OWNER', 'UUID', 'HOSTNAME']).issubset(violation_data), \
                'Invalid keys in violation_data'

            # Set email's recipients
            recipients = []
            intruder_username = violation_data['INTRUDER']
            intruder_email = self.fetch_email_address(username=intruder_username)

            if intruder_email and self.ready_to_send(intruder_email):
                recipients.append(intruder_email)
            if MAILBOT.NOTIFY_ADMIN and self.ready_to_send(MAILBOT.ADMIN_EMAIL):
                recipients.append(MAILBOT.ADMIN_EMAIL)
            assert recipients

            # Initialize mailer connection
            self.mailer.connect(
                login=os.getenv(MAILBOT.SMTP_LOGIN_ENV),
                password=os.getenv(MAILBOT.SMTP_PASSWORD_ENV)
            )

            # Prepare email and send
            email = self.prepare_message(violation_data, recipients)
            self.mailer.send(email)
        except AssertionError as e:
            pass
        except Exception as e:
            log.critical(e)
        else:
            log.debug('Email sent to: {}'.format(email.recipients))
            # Remember time email was sent
            for email_address in recipients:
                self.time_of_last_email[email_address] = datetime.datetime.utcnow()
            self.mailer.disconnect()
