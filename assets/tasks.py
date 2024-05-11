from django.conf import settings
from django_celery_beat.models import (
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    PeriodicTasks,
)

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import shared_task

import smtplib

from assets.backend import current_price
from assets.models import Asset


def compose_email(asset=None):
    symbol = asset.ticker.symbol
    mail_subject = f'Profit margin reached for {symbol}'
    mail_body = f"""
    Dear {asset.user.username}, 
    
    The profit margin was reached for {symbol}.
    
    You paid {asset.paid}$ for {asset.quantity} of {symbol}. With a current value of {asset.value}$, the goal 
    of reaching {asset.margin}$ profit is achieved and you cand exchange your {symbol}!

    Enjoy your money, and have a good day.
    
    This email was sent by LGSGS.
    """
    send_email.delay(to_email=asset.user.email, mail_subject=mail_subject, mail_body=mail_body)


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
        connection.login(username,password)
        connection.send_message(mimemsg)
        connection.quit()
        return True
    except Exception as e:
        connection.quit()
        return e


@shared_task
def update_prices():
    qs = Asset.objects.filter(monitor=True)
    for asset in qs:
        asset.current = current_price(asset.ticker.symbol)
        asset.save()
        if asset.target_reached:
            compose_email(asset=asset)

