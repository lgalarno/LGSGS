import ccxt
import http.client
import json

from coinbase import jwt_generator
from decimal import Decimal


def get_balance(credential=None):
    balance = False
    trader = credential.trader.name
    if trader == 'NDAX':
        ndax = ccxt.ndax()
        ndax.apiKey = credential.decrypt(todecrypt='apiKey')
        ndax.secret = credential.decrypt(todecrypt='secret')
        ndax.uid = credential.uid
        ndax.login = credential.unername
        ndax.password = credential.decrypt(todecrypt='password')
        ndax.twofa = credential.decrypt(todecrypt='twofa')
        ndax.enableRateLimit = False
        ndax.requiredCredentials
        try:
            ndax.sign_in()
            info = ndax.fetchBalance()
            fiat_account = info.get('CAD')
            if fiat_account:
                free = fiat_account.get('free')
                if free:
                    balance = Decimal(free).quantize(Decimal("1.00"))
        except:
            balance = 'Pas disponible'
    elif trader == 'Coinbase':
        api_key = credential.decrypt(todecrypt='apiKey')
        secret = credential.decrypt(todecrypt='secret')
        api_secret = f"-----BEGIN EC PRIVATE KEY-----\n{secret}\n-----END EC PRIVATE KEY-----\n"
        jwt_uri = jwt_generator.format_jwt_uri("GET", "/api/v3/brokerage/accounts")
        jwt_token = jwt_generator.build_rest_jwt(jwt_uri, api_key, api_secret)
        headers = {'Authorization': f'Bearer {jwt_token}', 'Content-Type': 'application/json'}
        payload = ''
        conn = http.client.HTTPSConnection("api.coinbase.com")
        try:
            conn.request("GET", "/api/v3/brokerage/accounts", payload, headers)
            res = conn.getresponse()
            data = res.read().decode('utf-8')
            json_obj = json.loads(data)
            accounts = json_obj.get("accounts")
            fiat_account = find('CAD Wallet', accounts)
            available_balance = fiat_account.get('available_balance')
            if available_balance:
                balance_str = available_balance.get('value')
                if balance_str:
                    balance = Decimal(float(balance_str)).quantize(Decimal("1.00"))
        except:
            balance = 'Pas disponible'
    return balance


def find(target, alist):
    for a in alist:
        if a.get('name') == target:
            return a
    return False
