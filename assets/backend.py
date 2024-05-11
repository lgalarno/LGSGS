import yfinance as yf


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
