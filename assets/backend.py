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
    try:
        data = yf.Ticker(s).history(period="1d")
        price = data["Close"].iloc[-1]
    except:
        price = 0
    return price


def update_prices(qs=None):
    if not qs:
        qs = Asset.objects.all()
    for asset in qs:
        cp = current_price(asset.ticker.symbol)
        if not asset.current == cp:
            asset.current = cp
            asset.save()
