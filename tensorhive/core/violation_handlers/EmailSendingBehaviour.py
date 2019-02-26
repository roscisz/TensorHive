from tensorhive.core.utils.decorators.override import override
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.models.User import User
from typing import Generator, Dict, List, Any, Optional
from tensorhive.config import MAILBOT
from tensorhive.core.utils.mailer import Mailer, Message, MessageBodyTemplater
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
        self.interval = datetime.timedelta(minutes=MAILBOT.INTERVAL)
        self.time_of_last_email = {}
        self.mailer = Mailer(server=MAILBOT.SMTP_SERVER, port=MAILBOT.SMTP_PORT)

    def filter_sessions(self, violation_data):
        result = []
        # self.time_between_notifications = time_left
        return result

    def prepare_intruder_message(self, violation_data: Dict[str, Any], recipients: List[str]) -> Message:
        email_body = MessageBodyTemplater(
            template=MAILBOT.INTRUDER_BODY_TEMPLATE
        ).fill_in(data=violation_data)

        return Message(
            author=MAILBOT.SMTP_LOGIN,
            to=recipients,
            subject=MAILBOT.INTRUDER_SUBJECT,
            body=email_body
        )

    def prepare_admin_message(self, violation_data: Dict[str, Any], recipients: List[str]) -> Message:
        email_body = MessageBodyTemplater(
            template=MAILBOT.INTRUDER_BODY_TEMPLATE
        ).fill_in(data=violation_data)

        return Message(
            author=MAILBOT.SMTP_LOGIN,
            to=recipients,
            subject=MAILBOT.INTRUDER_SUBJECT,
            body=email_body
        )

    def fetch_email_address(self, username: str) -> Optional[str]:
        email = None
        try:
            intruder = User.find_by_username(username)
        except NoResultFound:
            # User does not exist or has no email address
            pass
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
        except KeyError:
            ready_status = True
        finally:
            return ready_status

    # TODO Refactor these two clunky, redundant methods
    def send_email_to_intruder(self, violation_data: Dict[str, Any]):
        author = MAILBOT.SMTP_LOGIN
        recipient = violation_data['INTRUDER_EMAIL']
        email_body = MessageBodyTemplater(template=MAILBOT.INTRUDER_BODY_TEMPLATE).fill_in(data=violation_data)

        email = Message(
            author=author,
            to=[recipient],
            subject=MAILBOT.INTRUDER_SUBJECT,
            body=email_body
        )
        self.mailer.send(email)
        self.time_of_last_email[recipient] = datetime.datetime.utcnow()
        log.warning('Email sent to: {}'.format(recipient))

    def send_email_to_admin(self, violation_data: Dict[str, Any]):
        author = MAILBOT.SMTP_LOGIN
        recipient = MAILBOT.ADMIN_EMAIL
        email_body = MessageBodyTemplater(template=MAILBOT.ADMIN_BODY_TEMPLATE).fill_in(data=violation_data)

        email = Message(
            author=author,
            to=[recipient],
            subject=MAILBOT.ADMIN_SUBJECT,
            body=email_body
        )
        self.mailer.send(email)
        self.time_of_last_email[recipient] = datetime.datetime.utcnow()
        log.warning('Email sent to: {}'.format(recipient))

    @override
    def trigger_action(self, violation_data: Dict[str, Any]):
        # Expect proper keys beforehand
        assert set([
            'INTRUDER_USERNAME',
            'RESERVATION_OWNER_USERNAME',
            'RESERVATION_OWNER_EMAIL',
            'RESERVATION_END',
            'UUID',
            'HOSTNAME']).issubset(violation_data), 'Invalid keys in violation_data'
        # Initialize mailer connection
        self.mailer.connect(
            login=MAILBOT.SMTP_LOGIN,
            password=MAILBOT.SMTP_PASSWORD
        )
        try:
            # Fetch and store intruder's email
            intruder_email = self.fetch_email_address(username=violation_data['INTRUDER_USERNAME'])
            violation_data['INTRUDER_EMAIL'] = intruder_email

            # Send emails
            if intruder_email and self.ready_to_send(intruder_email):
                self.send_email_to_intruder(violation_data)
            if MAILBOT.NOTIFY_ADMIN and self.ready_to_send(MAILBOT.ADMIN_EMAIL):
                self.send_email_to_admin(violation_data)
        except AssertionError:
            pass
        except Exception as e:
            log.critical(e)
            import traceback
            traceback.print_exc()
        else:
            self.mailer.disconnect()
