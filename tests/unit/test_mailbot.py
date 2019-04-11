from tensorhive.core.violation_handlers.EmailSendingBehaviour import EmailSendingBehaviour
from tensorhive.models.User import User
from tensorhive.config import MAILBOT
from tensorhive.core.utils.mailer import MessageBodyTemplater, Message, Mailer
from datetime import datetime
from unittest.mock import patch
from typing import Any
import pytest
import email


@pytest.yield_fixture()
def violation_data():
    return {
        'INTRUDER_USERNAME': 'intruder_email_mock',
        'RESERVATION_OWNER_USERNAME': 'owner_username_mock',
        'RESERVATION_OWNER_EMAIL': 'owner_email_mock',
        'RESERVATION_END': 'datetime_mock',
        'UUID': 'uuid_mock_' * 4,
        'GPU_NAME': 'GPU mock',
        'HOSTNAME': 'Hostname mock'
    }


def test_mailer_when_try_to_send_before_connect():
    with pytest.raises(AssertionError):
        Mailer('foo', 123).send('foo')


def test_mailer_sending_with_invalid_message():
    with patch('smtplib.SMTP') as mock_smtp:
        mailer = Mailer('foo', 123)
        mailer.connect(login=Any, password=Any)
        with pytest.raises(AssertionError):
            message = Message(None, None, None, None)
            mailer.send(message)


def test_message_properly_processes_init_arguments():
    # Single recipient
    message = Message(author='foo', to='bar', subject='foo', body='bar')
    assert message.author == 'foo'
    assert message.recipients == 'bar'
    assert message.subject == 'foo'
    assert isinstance(message.msg, email.mime.multipart.MIMEMultipart)
    assert isinstance(message.body, str)

    # Multiple recipients
    message = Message(author='foo', to=['foo', 'bar', 'fizz'], subject='foo', body='bar')
    assert message.recipients == 'foo, bar, fizz'


def test_sendmail_is_reached_with_mock_smtp_server():
    with patch('smtplib.SMTP') as mock_smtp:
        mailer = Mailer('foo', 123)
        message = Message(author='foo', to='bar', subject='foo', body='bar')

        mailer.server = mock_smtp.return_value
        mailer.send(message)
        assert mailer.server.sendmail.call_count == 1

# Test that send real email (must check manually for now)
# def test_sending_real_email_to_inbox(violation_data):
#     MAILBOT.SMTP_SERVER = 'smtp.gmail.com'
#     MAILBOT.SMTP_PORT = 587
#     MAILBOT.SMTP_LOGIN = 'tensorhive.mailbot@gmail.com'
#     MAILBOT.SMTP_PASSWORD = '===REPLACE ME WITH REAL PASSWORD==='

#     MAILBOT.NOTIFY_ADMIN = True
#     MAILBOT.ADMIN_EMAIL = 'tensorhive.mailbot@gmail.com'
#     with patch.object(User, 'find_by_username') as mock_intruder:
#         mock_intruder.return_value.email = 'tensorhive.mailbot@gmail.com'
#         mailbot = EmailSendingBehaviour()
#         with patch.object(mailbot, '_time_to_resend') as mock_resend:
#             mock_resend.return_value = True
#             mailbot.trigger_action(violation_data)
