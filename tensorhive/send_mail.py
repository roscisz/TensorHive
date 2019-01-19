import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
 
 
fromaddr = "michal.martyniak@linux.pl"
toaddr = "michal.martyniak@linux.pl"
password = os.environ['MAIL_PASS']

msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "TensorHive bot"
 
body = "Alert!"
msg.attach(MIMEText(body, 'plain'))
 
server = smtplib.SMTP('mail.linux.pl', 587)
server.starttls()
server.login(fromaddr, password)
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()