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


def ticker_info(symbol, tickertype):
    """
    :param symbol: ticker symbol, tickertype: as of Ticker model: crypto or equity
    :return: if the ticker symbol exists, return its name; otherwise, return None
    """
    #TODO only support ndax and Yahoo finance tickers. Add others based on exchange?
    tinfo = {'error': False,
             'name': None,
             'symbol': symbol.upper()
             }
    if tickertype == 'crypto':
        ndax = ccxt.ndax({
            'enableRateLimit': True,
            # 'apiKey': NDAX_API_KEY
        })
        markets = ndax.load_markets()
        if tinfo['symbol'] in list(markets.keys()):
            tinfo['name'] = markets[tinfo['symbol']].get('base')
        else:
            tinfo['error'] = True
    else:
        ticker = yf.Ticker(tinfo['symbol'])
        info = ticker.info
        if info.get('symbol') is not None:
            tinfo['name'] = info.get('shortName')
        else:
            tinfo['error'] = True
    return tinfo


def ticker_name(symbol, tickertype):
    """
    :param symbol: ticker symbol, tickertype: as of Ticker model: crypto or equity
    :return: if the ticker symbol exists, return its name; otherwise, return None
    """
    #TODO only support ndax and Yahoo finance tickers. Add others based on exchange?
    name = None
    if tickertype == 'crypto':
        ndax = ccxt.ndax({
            'enableRateLimit': True,
            # 'apiKey': NDAX_API_KEY
        })
        markets = ndax.load_markets()
        if symbol in list(markets.keys()):
            name = markets[symbol].get('base')
    else:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        print(info.get('symbol'))
        if info.get('symbol') is not None:
            name = info.get('shortName')
    return name


def current_price(symbol, type, *args, **kwargs):
    """
    #### only support ndax tickers. add others based on exchange ####

    :param symbols: list of ticker symbols, crypto: boolean if crypto, true
    :return: price
    """
    # try:
    price = 0
    if type == "crypto":
        ndax = ccxt.ndax({
            'apiKey': NDAX_API_KEY,
            'enableRateLimit': False
        })
        try:
            price = ndax.fetch_ticker(symbol).get('last')
        except:
            price = 0
    else:
        data = yf.Ticker(symbol).history(period="1d")
        if data.empty:
            data = yf.Ticker(symbol).history(period="3d")  # 3d because sometime, days are skipped?
            #TODO write better code
            if data.empty:
                data = yf.Ticker(symbol).history(period="5d")  # 5d because sometime, days are skipped?
                if data.empty:
                    data = yf.Ticker(symbol).history(period="10d")  # 10d because sometime, days are skipped?
        if not data.empty:
            price = data["Close"].iloc[-1]
    # except:
    #     price = 0
    return price


def update_prices(qs=None):
    if not qs:  # automatic update task
        qs = Asset.objects.all()
    if qs:
        for asset in qs:
            t = asset.transaction
            cp = current_price(t.ticker.symbol, t.ticker.type)
            if not asset.current == cp:
                asset.current = cp
                asset.save()
