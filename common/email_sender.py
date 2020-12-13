import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailSender:
    def __init__(self, config):
        self.sender_email = config["email"]
        self.sender_name = config["name"]
        self.password = config["password"]

    def send_email(self, receiver_email, subject, body):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(self.sender_email, self.password)
            msg = MIMEMultipart()
            msg["From"] = self.sender_name
            msg["To"] = receiver_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))
            server.send_message(msg)
