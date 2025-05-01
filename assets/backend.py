from django.conf import settings
from django.utils import timezone

from dateutil.relativedelta import relativedelta
from django_celery_beat.models import PeriodicTask

from assets.models import Asset

import ccxt
import yfinance as yf


NDAX_API_KEY = settings.NDAX_API_KEY


def get_refresh_info() -> dict:
    pt = PeriodicTask.objects.filter(name='update_prices-30-minutes').last()  # name in celery.py
    if pt:
        min = 240 - settings.UPDT_INTERVAL  # 240 min = 4h from UTC
        last_updated = timezone.now() + relativedelta(minutes=-240)
        update_at = pt.last_run_at + relativedelta(minutes=-min)
    else:
        last_updated = None
        update_at = None
    return {
        'last_updated': last_updated,
        'update_at': update_at
    }


def ticker_name(symbol, tickertype):
    """
    :param symbol: ticker symbol, tickertype: as of Ticker model: crypto or equity
    :return: if the ticker symbol exists, return its name; otherwise, return None
    """
    #TODO only support ndax and Yahho finance tickers. Add others based on exchange?
    if tickertype == 'crypto':
        ndax = ccxt.ndax({
            'apiKey': NDAX_API_KEY
        })
        markets = ndax.load_markets()
        if symbol in list(markets.keys()):
            return markets[symbol].get('base')
    else:
        ticker = yf.Ticker(symbol)
        # info = None
        try:
            info = ticker.info
            name = info['shortName']
            return name
        except:
            return None
    return None


def current_price(symbol, crypto, *args, **kwargs):
    """
    #### only support ndax tickers. add others based on exchange ####

    :param symbols: list of ticker symbols, crypto: boolean if crypto, true
    :return: price
    """
    try:
        if crypto:
            ndax = ccxt.ndax({
                'apiKey': NDAX_API_KEY,
                'enableRateLimit': False
            })
            price = ndax.fetch_ticker(symbol).get('last')
        else:
            data = yf.Ticker(symbol).history(period="1d")
            price = data["Close"].iloc[-1]
    except:
        price = 0
    return price


def update_prices(qs=None):
    if not qs:
        qs = Asset.objects.all()
    for asset in qs:
        cp = current_price(asset.ticker.symbol, asset.is_crypto)
        if not asset.current == cp:
            asset.current = cp
            asset.save()
