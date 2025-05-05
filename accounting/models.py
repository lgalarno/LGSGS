from django.db import models

# from decimal import Decimal

from wallets.models import Wallet, Ticker

# Create your models here.


class DisnatBook(models.Model):
    wallet = models.ForeignKey(to=Wallet,on_delete=models.CASCADE, null=True, blank=True)
    date_de_transaction = models.DateField(null=True, blank=True)
    date_de_reglement = models.DateField()
    type_de_transaction = models.CharField(max_length=32, null=True, blank=True)
    classe_d_actif = models.CharField(max_length=32, null=True, blank=True)
    symbole = models.ForeignKey(to=Ticker, on_delete=models.CASCADE, null=True, blank=True)
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
    wallet = models.ForeignKey(to=Wallet, on_delete=models.CASCADE, null=True, blank=True)
    ticker = models.ForeignKey(to=Ticker, on_delete=models.CASCADE, null=True, blank=True)
    number_id = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    price_buy= models.DateField(null=True, blank=True)
    price_sold = models.DateField(null=True, blank=True)
    profit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    date_buy= models.DateField(null=True, blank=True)
    date_sold = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-date_sold']

    def __str__(self):
        return f"{self.wallet.name}"
