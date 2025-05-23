from django.conf import settings

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import shared_task

import smtplib


@shared_task
def send_email(to_email, mail_subject, mail_body):
    username = settings.FROM_EMAIL
    password = settings.EMAIL_PASSWORD

    mimemsg = MIMEMultipart()
    mimemsg['From'] = username
    mimemsg['To'] = to_email
    mimemsg['Subject'] = mail_subject
    mimemsg.attach(MIMEText(mail_body, 'plain'))
    try:
        with smtplib.SMTP('smtp.mail.yahoo.com', 587) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(mimemsg)
        return True
    except Exception as e:
        return e


@shared_task
def update_prices_task():
    from assets.backend import update_prices
    update_prices()


