from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Union, Dict, Any, Optional, List
import smtplib
from smtplib import SMTPException
import os
import logging
log = logging.getLogger(__name__)


class Message:
    '''
    Represents an email message.
    Allows for sending to a copy to multiple recipients.
    Send using the Mailer class.
    '''

    def __init__(self, author: str, to: Union[str, List[str]], subject: str, body: str):
        msg = MIMEMultipart()
        msg['From'] = author
        msg['To'] = ', '.join(to) if isinstance(to, list) else to
        msg['Subject'] = subject
        msg.attach(MIMEText(body or '', 'html'))
        self.msg = msg

    @property
    def author(self):
        return self.msg['From']

    @property
    def recipients(self):
        return self.msg['To']

    @property
    def subject(self):
        return self.msg['Subject']

    @property
    def body(self):
        return self.msg.as_string()

    def __str__(self):
        return '''
            From: {}
            To: {}
            Subject: {}
            Body: {}
            '''.format(self.author, self.recipients, self.subject, self.body)


class MessageBodyTemplater:
    def __init__(self, template: str):
        self.template = template

    def fill_in(self, data: Dict[str, Any]) -> str:
        return self.template.format(
            hostname=data['HOSTNAME'],
            gpu_id=data['GPU_ID'],
            gpu_name=data['GPU_NAME'],
            gpu_uuid=data['UUID'],
            intruder_username=data['INTRUDER_USERNAME'],
            intruder_email=data['INTRUDER_EMAIL'],
            owner_username=data['RESERVATION_OWNER_USERNAME'],
            owner_email=data['RESERVATION_OWNER_EMAIL'],
            reservation_end=data['RESERVATION_END'],
        )


class Mailer:
    def __init__(self, server: str, port: int) -> None:
        self.smtp_server = server
        self.smtp_port = port
        self.server = None  # type: smtplib.SMTP

    def send(self, message: Message) -> None:
        assert self.server, 'Must call connect() first!'
        assert message.author and message.recipients and message.body, 'Incomplete email body: {}'.format(message)
        try:
            self.server.sendmail(message.author, message.recipients, message.body)
        except SMTPException as e:
            log.error('Error while sending email: {}'.format(e))

    def connect(self, login: str, password: str) -> None:
        # assert login and password, 'Login and password must not be None!'
        # assert self.smtp_server and self.smtp_port, 'SMTP server and port must not be None!'
        self.server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        self.server.starttls()
        self.server.login(login, password)

    def disconnect(self) -> None:
        self.server.close()
