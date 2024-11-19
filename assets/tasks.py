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
        connection = smtplib.SMTP(host='smtp.office365.com', port=587)
        connection.starttls()
        connection.login(username, password)
        connection.send_message(mimemsg)
        connection.quit()
        return True
    except Exception as e:
        connection.quit()
        return e


@shared_task
def update_prices_task():
    from assets.backend import update_prices
    update_prices()
    # for asset in qs:
    #     asset.current = current_price(asset.ticker.symbol)
    #     if asset.target_reached and not asset.emailed:
    #         compose_email(asset=asset)
    #         asset.emailed = True
    #     asset.save()

