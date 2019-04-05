from tensorhive.core.utils.decorators.override import override
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.models.User import User
from typing import Generator, Dict, List, Any, Optional
from tensorhive.config import MAILBOT, CONFIG_FILES
from tensorhive.core.utils.mailer import Mailer, Message, MessageBodyTemplater
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from inspect import cleandoc
import datetime
import smtplib
import logging
log = logging.getLogger(__name__)


class LastEmailTime:
    '''TODO'''

    def __init__(self):
        self.to_admin = datetime.datetime.min
        self.to_intruder = datetime.datetime.min


class EmailSendingBehaviour:
    '''TODO'''

    def __init__(self) -> None:
        '''TODO'''
        self.mailer = Mailer(server=MAILBOT.SMTP_SERVER, port=MAILBOT.SMTP_PORT)
        self.test_smtp_configuration()
        self.interval = datetime.timedelta(minutes=MAILBOT.INTERVAL)
        self.timers = {}

    def time_to_resend(self, timer: LastEmailTime, to_admin: Optional[bool] = False) -> bool:
        '''TODO'''
        if to_admin:
            last_notification_time = timer.to_admin
        else:
            last_notification_time = timer.to_intruder
        return last_notification_time + self.interval <= datetime.datetime.utcnow()

    def get_timer(self, keyname: str) -> Dict[str, datetime.datetime]:
        '''TODO'''
        try:
            timer = self.timers[keyname]
        except KeyError:
            self.timers[keyname] = LastEmailTime()
            return self.timers[keyname]
        else:
            return timer

    def test_smtp_configuration(self) -> bool:
        try:
            assert MAILBOT.SMTP_SERVER and MAILBOT.SMTP_PORT, 'Incomplete SMTP server configuration'
            assert MAILBOT.SMTP_LOGIN and MAILBOT.SMTP_PASSWORD, 'Incomplete SMTP server credentials'
            if MAILBOT.NOTIFY_ADMIN:
                assert MAILBOT.ADMIN_EMAIL, 'Admin contact email not specified despite enabled notifications'

            self.mailer.connect(login=MAILBOT.SMTP_LOGIN, password=MAILBOT.SMTP_PASSWORD)
        except AssertionError as e:
            log.error('{}, please check your config: {}'.format(e, CONFIG_FILES.MAILBOT_CONFIG_PATH))
            return False
        except smtplib.SMTPException as e:
            log.error(e)
            return False
        else:
            return True

    def email_intruder(self, email: str, violation_data: Dict, timer: LastEmailTime) -> None:
        email_body = MessageBodyTemplater(template=MAILBOT.INTRUDER_BODY_TEMPLATE).fill_in(data=violation_data)
        email = Message(author=MAILBOT.SMTP_LOGIN, to=email, subject=MAILBOT.INTRUDER_SUBJECT, body=email_body)
        self.mailer.send(email)
        timer.to_intruder = datetime.datetime.utcnow()
        log.info('Email to intruder has been sent: {}'.format(email))

    def email_admin(self, violation_data: Dict, timer: LastEmailTime) -> None:
        email_body = MessageBodyTemplater(template=MAILBOT.ADMIN_BODY_TEMPLATE).fill_in(data=violation_data)
        email = Message(author=MAILBOT.SMTP_LOGIN, to=MAILBOT.ADMIN_EMAIL,
                        subject=MAILBOT.ADMIN_SUBJECT, body=email_body)
        self.mailer.send(email)
        timer.to_admin = datetime.datetime.utcnow()
        log.info('Email to admin has been sent: {}'.format(email))

    @override
    def trigger_action(self, violation_data: Dict[str, Any]) -> None:
        '''TODO'''
        # Expect proper keys beforehand
        assert {
            'INTRUDER_USERNAME',
            'RESERVATION_OWNER_USERNAME',
            'RESERVATION_OWNER_EMAIL',
            'RESERVATION_END',
            'UUID',
            'HOSTNAME'}.issubset(violation_data), 'Invalid keys in violation_data'

        if not self.test_smtp_configuration():
            return

        try:
            # Fetch email address and extend violation data
            intruder_email = User.find_by_username(violation_data['INTRUDER_USERNAME']).email
        except NoResultFound as e:
            intruder_email = None
            log.warning(e)
        finally:
            violation_data['INTRUDER_EMAIL'] = intruder_email

        if not intruder_email:
            # At least try notify admin
            timer = self.get_timer(violation_data['INTRUDER_USERNAME'])
            if MAILBOT.NOTIFY_ADMIN and self.time_to_resend(timer, to_admin=True):
                self.email_admin(violation_data, timer)
            return

        # Try email both
        timer = self.get_timer(intruder_email)
        if MAILBOT.NOTIFY_INTRUDER and self.time_to_resend(timer):
            self.email_intruder(intruder_email, violation_data, timer)
        if MAILBOT.NOTIFY_ADMIN and self.time_to_resend(timer, to_admin=True):
            self.email_admin(violation_data, timer)
