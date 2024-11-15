from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone

from decimal import Decimal

from assets.models import Ticker, Trader, Asset

# Create your models here.


class Wallet(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=120, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    lastviewed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{str(self.user)}-{self.name}"  # str(self.user)


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
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    )
    CURRENCY = (
        ('cad', 'CAD'),
        ('usd', 'USD'),
    )
    type = models.CharField(max_length=10, choices=TYPE, default=TYPE[0][0])
    wallet = models.ForeignKey(to=Wallet, on_delete=models.CASCADE)
    asset = models.OneToOneField(to=Asset, related_name='transaction', on_delete=models.SET_NULL, null=True, blank=True)
    ticker = models.ForeignKey(to=Ticker, related_name='transaction', on_delete=models.CASCADE)
    trader = models.ForeignKey(to=Trader, related_name='transaction', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=14, decimal_places=8, validators=[MinValueValidator(0.0)])
    quantity = models.FloatField(validators=[MinValueValidator(0.0)])
    currency = models.CharField(max_length=4, choices=CURRENCY, default=TYPE[0][0])
    change = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0.0)], default=0)
    fees = models.DecimalField(max_digits=14, decimal_places=8, validators=[MinValueValidator(0.0)], default=0)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date}-{self.type}-{self.ticker.symbol}"

    def get_absolute_url(self):
        return reverse('wallets:wallets-htmx-api:transaction', kwargs={'pk': self.pk})

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
                            + float(self.fees))).quantize(Decimal("1.00"))
        else:
            return 0

    @property
    def total_revenue(self):
        if self.type == 'sell':
            return Decimal((self.quantity * float(self.price) + float(self.change)
                            - float(self.fees))).quantize(Decimal("1.00"))
        else:
            return 0

    @property
    def price_per_share(self):
        if self.type == 'buy':
            if self.ticker.type =='crypto':
                return self.paid / (self.quantity - float(self.fees))  # (float(self.fees) + float(self.change)) / self.quantity + float(self.price)
            elif self.ticker.type == 'equity':
                return (float(self.fees) + float(self.change)) / self.quantity + float(self.price)
        return 0

    @property
    def paid(self, quantity=None):
        if quantity is None:
            quantity = self.quantity
        return quantity * float(self.price)


class Profit(models.Model):
    transaction_bought = models.ForeignKey(to=Transaction, related_name='bought', on_delete=models.CASCADE)
    transaction_sold = models.ForeignKey(to=Transaction, related_name='sold', on_delete=models.CASCADE)
    profit = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0.0)])
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return f"{self.transaction_sold.date}-{self.transaction_sold.ticker.symbol}-{self.transaction_sold.wallet.name}"

    @property
    def marginal_cost(self):
        return Decimal(self.transaction_sold.quantity * float(self.transaction_bought.price_per_share)).quantize(Decimal("1.00"))

    @property
    def marginal_profit(self):
        return Decimal(self.transaction_sold.total_revenue - self.marginal_cost).quantize(Decimal("1.00"))
