from django.db import models

from decimal import Decimal

from wallets.models import Wallet, Ticker

# Create your models here.


class DisnatBook(models.Model):
    wallet = models.ForeignKey(to=Wallet,on_delete=models.CASCADE, null=True, blank=True)
    date_de_transaction = models.DateField(null=True, blank=True)
    date_de_reglement = models.DateField()
    type_de_transaction = models.CharField(max_length=32, null=True, blank=True)
    classe_d_actif = models.CharField(max_length=32, null=True, blank=True)
    symbole = models.CharField(max_length=16, null=True, blank=True)
    description = models.CharField(max_length=128, null=True, blank=True)
    marche = models.CharField(max_length=8, null=True, blank=True)
    quantite = models.IntegerField(null=True, blank=True)
    prix = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    devise_du_prix = models.CharField(max_length=8, null=True, blank=True)
    commission_payee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    montant_de_l_operation = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    devise_du_compte = models.CharField(max_length=8, null=True, blank=True)
    numero_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['date_de_reglement']

    def __str__(self):
        return f"{self.wallet.name} {self.date_de_reglement} {self.type_de_transaction} {self.symbole}"


class CryptoBook(models.Model):
    TYPE = (
        ('purchase', 'Purchase'),
        ('sell', 'Sell'),
    )
    wallet = models.ForeignKey(to=Wallet, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE, default=TYPE[0][0])
    ticker = models.CharField(max_length=16, null=True, blank=True)
    number_id = models.IntegerField(null=True, blank=True)
    quantity = models.FloatField( null=True, blank=True)
    price = models.DecimalField(max_digits=14, decimal_places=10, null=True, blank=True)
    fees = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    date = models.DateField()

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.wallet.name} {self.date} {self.type} {self.ticker}"

    def total_price(self):
        total_price = self.quantity * float(self.price)
        return Decimal(total_price).quantize(Decimal("1.00"))

    def fees_in_money(self):
        fees_in_money = 0
        if self.wallet.trader.fees_sell == "money" and self.type == 'sell':
            fees_in_money = self.fees
        elif self.wallet.trader.fees_sell == "crypto" and self.type == 'sell':
            fees_in_money = float(self.price) * self.quantity
        elif self.wallet.trader.fees_buy == "crypto" and self.type == 'purchase':
            fees_in_money = float(self.price) * self.quantity
        elif self.wallet.trader.fees_sell == "money" and self.type == 'purchase':
            fees_in_money = self.fees
        return Decimal(fees_in_money).quantize(Decimal("1.00"))
