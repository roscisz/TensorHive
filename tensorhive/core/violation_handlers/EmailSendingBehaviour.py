from tensorhive.core.utils.decorators import override
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
    '''Simple struct-like class that allows remembering when X were last emailed.
    Each intruder has it's own timer for notifying admin.
    '''

    def __init__(self):
        self.to_admin = datetime.datetime.min
        self.to_intruder = datetime.datetime.min


class EmailSendingBehaviour:
    '''
    When violation is triggered by ProtectionHandler it tries to contact
    intruder and/or admin via email.

    They get individual email message based on different HTML templates.
    It will send messages periodically (every `self.interval` time)

    There is `self.timers` memory which stores who and when was recentyl emailed.
    If intruder does not have email assigned (or no account at all),
    only admin will be notified (MAILBOT.NOTIFY_ADMIN and MAILBOT.ADMIN_EMAIL must be configured)

    If SMTP configuration (server or credentials) are incorrect,
    it will be logged each time `trigger_action` is called.
    '''

    def __init__(self) -> None:
        self.mailer = Mailer(server=MAILBOT.SMTP_SERVER, port=MAILBOT.SMTP_PORT)
        self._test_smtp_configuration()
        self.interval = datetime.timedelta(minutes=MAILBOT.INTERVAL)
        self.timers = {}  # type: Dict[str, LastEmailTime]

    @override
    def trigger_action(self, violation_data: Dict[str, Any]) -> None:
        '''Contains business logic for intruder and admin email notifications.
        It relies on early returns if any error occures.

        :param violation_data: data received from ProtectionService
        '''
        # Expect certain keys beforehand
        assert {'INTRUDER_USERNAME', 'RESERVATION_OWNER_USERNAME',
                'RESERVATION_OWNER_EMAIL', 'RESERVATION_END', 'UUID', 'HOSTNAME'
                }.issubset(violation_data), 'Invalid keys in violation_data'

        if not self._test_smtp_configuration():
            return

        try:
            # Fetch intruder email address and extend violation data
            intruder_email = User.find_by_username(violation_data['INTRUDER_USERNAME']).email
        except NoResultFound as e:
            intruder_email = None
            log.warning(e)
        finally:
            violation_data['INTRUDER_EMAIL'] = intruder_email

        if not intruder_email:
            # Intruder has no account or email assigned, try notify admin then
            timer = self._get_timer(violation_data['INTRUDER_USERNAME'])
            if MAILBOT.NOTIFY_ADMIN and self._time_to_resend(timer, to_admin=True):
                self._email_admin(violation_data, timer)
            return

        # Intruder has account and email address, try email him and admin then
        timer = self._get_timer(intruder_email)
        if MAILBOT.NOTIFY_INTRUDER and self._time_to_resend(timer):
            self._email_intruder(intruder_email, violation_data, timer)
        if MAILBOT.NOTIFY_ADMIN and self._time_to_resend(timer, to_admin=True):
            self._email_admin(violation_data, timer)

    def _time_to_resend(self, timer: LastEmailTime, to_admin: Optional[bool] = False) -> bool:
        '''Returns whether last email was sent min X time ago.'''
        if to_admin:
            last_notification_time = timer.to_admin
        else:
            last_notification_time = timer.to_intruder
        return last_notification_time + self.interval <= datetime.datetime.utcnow()

    def _get_timer(self, keyname: str) -> LastEmailTime:
        '''Safe dict fetching. It will create missing key with default value.'''
        try:
            timer = self.timers[keyname]
        except KeyError:
            self.timers[keyname] = LastEmailTime()
            return self.timers[keyname]
        else:
            return timer

    def _test_smtp_configuration(self) -> bool:
        '''Does very basic checks whether config variables are not None (which is the default).
        Then, it tries to establish an SMTP connection.
        It logs error reason and appropriate hint.
        '''
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

    def _email_intruder(self, email_address: str, violation_data: Dict, timer: LastEmailTime) -> None:
        '''Prepare message, send and update timer.'''
        email_body = MessageBodyTemplater(template=MAILBOT.INTRUDER_BODY_TEMPLATE).fill_in(data=violation_data)
        email = Message(author=MAILBOT.SMTP_LOGIN, to=email_address, subject=MAILBOT.INTRUDER_SUBJECT, body=email_body)
        self.mailer.send(email)
        timer.to_intruder = datetime.datetime.utcnow()
        log.info('Sending email to intruder ({}) has been attempted.'.format(email_address))

    def _email_admin(self, violation_data: Dict, timer: LastEmailTime) -> None:
        '''Prepare message, send and update timer.'''
        email_body = MessageBodyTemplater(template=MAILBOT.ADMIN_BODY_TEMPLATE).fill_in(data=violation_data)
        email = Message(author=MAILBOT.SMTP_LOGIN, to=MAILBOT.ADMIN_EMAIL,
                        subject=MAILBOT.ADMIN_SUBJECT, body=email_body)
        self.mailer.send(email)
        timer.to_admin = datetime.datetime.utcnow()
        log.info('Sending email to admin ({}) has been attempted.'.format(MAILBOT.ADMIN_EMAIL))
