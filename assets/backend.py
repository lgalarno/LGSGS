from django.conf import settings
from django.utils import timezone

from dateutil.relativedelta import relativedelta
from django_celery_beat.models import PeriodicTask

from assets.models import Asset

import yfinance as yf


def get_refresh_info() -> dict:
    pt = PeriodicTask.objects.get(name='update_prices-30-minutes')  # name in celery.py
    min = 240 - settings.UPDT_INTERVAL
    return {
        'last_updated': timezone.now() + relativedelta(minutes=-240),
        'update_at': pt.last_run_at + relativedelta(minutes=-min)
    }


def ticker_name(symbol):
    """
    :param symbol: ticker symbo
    :return: if the ticker symbol exists, return its name; otherwise, return None
    """
    ticker = yf.Ticker(symbol)
    info = None
    try:
        info = ticker.info
        name = info['shortName']
        return name
    except:
        return None


def current_price(s):
    # try:
    print(s)
    data = yf.Ticker(s).history(period="1d")
    price = data["Close"].iloc[-1]
    # except:
    #     price = 0
    return price


# def compose_email(asset=None):
#     symbol = asset.ticker.symbol
#     mail_subject = f'Profit margin reached for {symbol}'
#     mail_body = f"""
#     Dear {asset.user.username},
#
#     The profit margin was reached for {symbol}.
#
#     You paid {asset.paid}$ for {asset.quantity} of {symbol}. With a current value of {asset.value}$, the goal
#     of reaching {asset.margin}$ profit is achieved and you cand exchange your {symbol}!
#
#     Enjoy your money, and have a good day.
#
#     This email was sent by LGSGS.
#     """
#     send_email.delay(to_email=asset.user.email, mail_subject=mail_subject, mail_body=mail_body)


def update_prices(qs=None):
    if not qs:
        qs = Asset.objects.filter(monitor=True)
    for asset in qs:
        if asset.monitor:
            asset.current = current_price(asset.ticker.symbol)
            # if asset.target_reached and not asset.emailed:
            #     compose_email(asset=asset)
            #     asset.emailed = True
            asset.save()
