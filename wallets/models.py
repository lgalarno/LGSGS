from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.dispatch import receiver
from django.shortcuts import reverse
from django.utils import timezone

from decimal import Decimal

from wallets.backend import get_balance
from assets.models import Asset

# Create your models here.


def upload_location(instance, filename):
    # keep for compatibility with migrations
    return f"logos/{filename}"


class TradingPlatform(models.Model):
    NAME = (
        ('Disnat', 'Disnat'),
        ('NDAX', 'NDAX'),
        ('Coinbase', 'Coinbase'),
    )
    URL = (
        ('https://www.disnat.com/', 'https://www.disnat.com/'),
        ('https://portal.ndax.io/', 'https://portal.ndax.io/'),
        ('https://www.coinbase.com/', 'https://www.coinbase.com/'),
    )
    LOGO = (
        ('images/logos/logo-courtage-ligne-fr.png', 'images/logos/logo-courtage-ligne-fr.png'),
        ('images/logos/ndax.png', 'images/logos/ndax.png'),
        ('images/logos/coinbase.png', 'images/logos/coinbase.png',),
    )
    FEES = (
        ('money', 'Monnaie'),
        ('crypto', 'Crypto'),
    )
    TYPE = (
        ('crypto', 'Crypto'),
        ('equity', 'Action'),
    )
    name = models.CharField(max_length=32,  choices=NAME, default=NAME[0][0])
    type = models.CharField(max_length=20, choices=TYPE, default=TYPE[0][0])
    logo = models.FileField(choices=LOGO, default=LOGO[0][0], null=True, blank=True)  # (max_length=255, choices=LOGO, default=LOGO[0][0], null=True, blank=True)
    url = models.URLField(blank=True, null=True, choices=URL, default=URL[0][0])
    fees_buy = models.CharField(max_length=20, choices=FEES, default=FEES[0][0])
    fees_sell = models.CharField(max_length=20, choices=FEES, default=FEES[0][0])

    def __str__(self):
        return self.name


@receiver(models.signals.pre_save, sender=TradingPlatform)
def complete_instance(sender, instance, *args, **kwargs):
    t = instance.name
    if t == 'Disnat':
        instance.type = 'equity'
        instance.logo = 'images/logos/logo-courtage-ligne-fr.png'
        instance.url = 'https://www.disnat.com/'
        instance.fees_buy = 'money'
        instance.fees_sell = 'money'
    elif t == 'Coinbase':
        instance.type = 'crypto'
        instance.logo = 'images/logos/coinbase.png'
        instance.url = 'https://www.coinbase.com/'
        instance.fees_buy = 'money'
        instance.fees_sell = 'money'
    elif t == 'NDAX':
        instance.type = 'crypto'
        instance.logo = 'images/logos/ndax.png'
        instance.url = 'https://portal.ndax.io/'
        instance.fees_buy = 'crypto'
        instance.fees_sell = 'money'


# class TradingPlatform(models.Model):
#     FEES = (
#         ('money', 'Monnaie'),
#         ('crypto', 'Crypto'),
#     )
#     TYPE = (
#         ('crypto', 'Crypto'),
#         ('equity', 'Action'),
#     )
#
#     name = models.CharField(max_length=255, null=True, blank=True)
#     type = models.CharField(max_length=20, choices=TYPE, default=TYPE[0][0])
#     logo = models.ImageField(upload_to=upload_location,
#                              null=True,
#                              blank=True)
#     url = models.URLField(blank=True, null=True)
#     fees_buy = models.CharField(max_length=20, choices=FEES, default=FEES[0][0])
#     fees_sell = models.CharField(max_length=20, choices=FEES, default=FEES[0][0])
#
#     def __str__(self):
#         return self.name


# @receiver(models.signals.post_delete, sender=TradingPlatform)
# def auto_delete_file_on_delete(sender, instance, **kwargs):
#     """
#     Deletes file from filesystem
#     when corresponding `Player` object is deleted.
#     """
#     if instance.logo:
#         if os.path.isfile(instance.logo.path):
#             os.remove(instance.logo.path)
#
#
# @receiver(models.signals.pre_save, sender=TradingPlatform)
# def auto_delete_file_on_change(sender, instance, **kwargs):
#     """
#     Deletes old file from filesystem
#     when corresponding `Player` object is updated
#     with new file.
#     """
#     if not instance.pk:
#         return False
#     try:
#         old_logo = TradingPlatform.objects.get(pk=instance.pk).logo
#     except TradingPlatform.DoesNotExist:
#         return False
#     new_logo = instance.logo
#     if not bool(old_logo):
#         return False
#     if not old_logo == new_logo:
#         if os.path.isfile(old_logo.path):
#             os.remove(old_logo.path)


class Ticker(models.Model):
    TYPE = (
        ('crypto', 'Crypto'),
        ('equity', 'Action'),
    )
    symbol = models.CharField(max_length=16)
    name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE, default=TYPE[0][0])

    class Meta:
        ordering = ['symbol']

    def __str__(self):
        return self.symbol

    def get_absolute_url(self):
        if self.type == 'equity':
            url = f"https://ca.finance.yahoo.com/quote/{self.symbol}/"
        else:
            url = reverse("wallets:detail-ticker", kwargs={"pk": self.pk})
        return url


class Wallet(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    trader = models.ForeignKey(to=TradingPlatform, related_name='wallet', on_delete=models.CASCADE, null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    balance_date = models.DateField(default=timezone.now)
    asset = models.ManyToManyField(to=Asset, related_name='wallet', blank=True)
    last_view = models.CharField(max_length=16, null=True, blank=True)
    last_viewed = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{str(self.user)}-{self.name}"  # str(self.user)

    @property
    def is_crypto(self):
        return self.trader.type == "crypto"

    @property
    def book_url(self):
        if self.is_crypto:
            return reverse("accounting:book-crypto", kwargs={"pk": self.pk})
        else:
            return reverse("accounting:book-disnat", kwargs={"pk": self.pk})

    @property
    def credentials(self):
        try:
            tc = self.trader.credentials.filter(user=self.user).get()
        except:
            tc = None
        return tc


@receiver(models.signals.post_save, sender=Wallet)
def update_balance(sender, instance, created, *args, **kwargs):
    tc = instance.credentials
    if tc:
        balance = get_balance(credential=tc)
        if not balance == 'Pas disponible':
            instance.balance = balance
            instance.balance_date = timezone.now().date()
            instance.save()


class Transfer(models.Model):
    TYPE = (
        ('deposit', 'Deposit'),
        ('interest', 'Interest'),
        ('dividends', 'Dividends'),
        ('withdrawal', 'Withdrawal'),
    )
    wallet = models.ForeignKey(to=Wallet, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE, default=TYPE[0][0])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    date = models.DateField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{str(self.wallet.name)}-{str(self.amount)}$"


class Transaction(models.Model):
    TYPE = (
        ('buy', 'Achat'),
        ('sell', 'Vente'),
    )
    CURRENCY = (
        ('cad', 'CAD'),
        ('usd', 'USD'),
    )
    type = models.CharField(max_length=10, choices=TYPE, default=TYPE[0][0])
    wallet = models.ForeignKey(to=Wallet, on_delete=models.CASCADE)
    asset = models.OneToOneField(to=Asset, related_name='transaction', on_delete=models.SET_NULL, null=True, blank=True)
    ticker = models.ForeignKey(to=Ticker, related_name='transaction', on_delete=models.CASCADE, null=True, blank=True)
    trading_platform = models.ForeignKey(to=TradingPlatform, related_name='transaction', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=14, decimal_places=8, validators=[MinValueValidator(0.0)])
    quantity = models.FloatField(validators=[MinValueValidator(0.0)])
    currency = models.CharField(max_length=4, choices=CURRENCY, default=CURRENCY[0][0])
    change = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0.0)], default=0)
    fees = models.DecimalField(max_digits=14, decimal_places=8, validators=[MinValueValidator(0.0)], default=0)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        #return f"{self.date}-{self.type}-{self.ticker.symbol}"
        return f"{self.date}"

    def get_absolute_url(self):
        return reverse('wallets:wallets-htmx-api:transaction', kwargs={'pk': self.pk})

    @property
    def is_crypto(self):
        return self.ticker.type == "crypto"

    @property
    def fees_in_dollars(self):
        if (self.wallet.trader.fees_sell == "crypto" and self.type == 'sell') or (self.wallet.trader.fees_buy == "crypto" and self.type == 'buy'):
            fees = Decimal(self.price * self.fees).quantize(Decimal("1.00"))
        else:
            fees = self.fees.normalize()
        return fees

    @property
    def get_fees(self):
        return self.fees.normalize()

    @property
    def get_price(self):
        return self.price.normalize()

    @property
    def brut(self):
        brut = self.quantity * float(self.price) + float(self.change)
        if self.ticker.type == 'equity':
            brut = brut + float(self.fees)
        return Decimal(brut).quantize(Decimal("1.00"))

    @property
    def total_paid(self):
        if self.type == 'buy':
            return Decimal((self.quantity * float(self.price) + float(self.change)
                            + float(self.fees_in_dollars))).quantize(Decimal("1.00"))
        else:
            return 0

    @property
    def total_revenue(self):
        if self.type == 'sell':
            total = Decimal((self.quantity * float(self.price) + float(self.change)
                             - float(self.fees_in_dollars))).quantize(Decimal("1.00"))
        # if self.type == 'sell':
        #     if self.trading_platform.fees_sell == 'money':
        #         total = Decimal((self.quantity * float(self.price) + float(self.change)
        #                          - float(self.fees))).quantize(Decimal("1.00"))
        #     elif self.trading_platform.fees_sell == 'crypto':
        #         q = self.quantity - self.fees
        #         total = Decimal(q * float(self.price) + float(self.change))
            return total
        else:
            return 0

    @property
    def price_per_share(self):
        if self.type == 'buy':
            p = (float(self.fees_in_dollars) + float(self.change)) / self.quantity + float(self.price)
            return Decimal(p).quantize(Decimal("1.0000000000")).normalize()
            # if self.trading_platform.fees_buy == 'crypto':
            #     return self.value / (self.quantity - float(self.fees))
            # elif self.trading_platform.fees_buy == 'money':
            #     return (float(self.fees) + float(self.change)) / self.quantity + float(self.price)
        return 0

    @property
    def value(self, quantity=None):
        if quantity is None:
            quantity = self.quantity
        return quantity * float(self.price)

    @property
    def fees_type(self):
        if self.type == 'buy':
            fees_type = self.trading_platform.fees_buy
        elif self.type == 'sell':
            fees_type = self.trading_platform.fees_sell
        else:
            fees_type = None
        return fees_type

    @property
    def get_fees_type(self):
        if self.type == 'buy':
            fees_type = self.trading_platform.fees_buy
        elif self.type == 'sell':
            fees_type = self.trading_platform.fees_sell
        else:
            fees_type = None
        if fees_type == 'crypto':
            s = self.ticker.symbol
        elif fees_type == 'money':
            s = '$'
        else:
            s = 'unknown'
        return s


class Profit(models.Model):
    transaction_bought = models.ForeignKey(to=Transaction, related_name='bought', on_delete=models.CASCADE)
    transaction_sold = models.ForeignKey(to=Transaction, related_name='sold', on_delete=models.CASCADE)
    profit = models.DecimalField(max_digits=14, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return f"{self.transaction_sold.date}-{self.transaction_sold.ticker.symbol}-{self.transaction_sold.wallet.name}"

    @property
    def marginal_cost(self):
        return Decimal(self.transaction_sold.quantity * float(self.transaction_bought.price_per_share)).quantize(Decimal("1.00"))

    @property
    def marginal_profit(self):
        return Decimal(self.transaction_sold.total_revenue - self.marginal_cost).quantize(Decimal("1.00"))
