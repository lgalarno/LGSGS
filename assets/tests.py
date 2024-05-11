from django.conf import settings
from django.test import TestCase

import yfinance as yf

from assets.models import Asset, Ticker
from accounts.models import User
# Create your tests here.


class GetPriceTestCase(TestCase):

    def setUp(self):
        u = User.objects.create(username="luc", email="lgalarno@gmail.com")
        u.save()

        t = Ticker.objects.create(symbol="AAPL")
        t.save()
        t1 = Ticker.objects.create(symbol="SOL-CAD")
        t1.save()

        asset = Asset.objects.create(
            user=u,
            ticker=t,
            description="",
            quantity=1,
            price=500,
            margin=10
        )
        asset.save()
        asset = Asset.objects.create(
            user=u,
            ticker=t,
            description="",
            quantity=1,
            price=500,
            margin=10,
            monitor=False
        )
        asset.save()
        asset = Asset.objects.create(
            user=u,
            ticker=t1,
            description="",
            quantity=1,
            price=500,
            margin=10
        )
        asset.save()

    def test_price_update(self):
        def current_price(s):
            try:
                data = yf.Ticker(s).history(period="1d")
                return data["Close"].iloc[-1]
            except:
                return 0

        u = User.objects.get(username="luc")
        qs = Asset.objects.filter(monitor=True)
        self.assertEqual(qs.count(), 2)
        for asset in qs:
            updt = current_price(asset.ticker.symbol)
            print(updt)
            self.assertNotEquals(0, updt)
