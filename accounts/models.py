from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
# from django.db.models import Sum

from accounts.backend import encrypt, decrypt
from wallets.models import TradingPlatform
# Create your models here.


class User(AbstractUser):
    website = models.URLField(blank=True, verbose_name='External portfolio url')
    country = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return self.username
    #
    # def total_balance(self):
    #     wallets = self.wallet_set.all()
    #     return wallets.aggregate(Sum('balance', default=0))['balance__sum']
#


class TraderCredentials(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    trader = models.ForeignKey(to=TradingPlatform, related_name='credentials', on_delete=models.CASCADE, null=True,
                               blank=True)
    unername = models.CharField(max_length=128, blank=True, null=True)
    password = models.CharField(max_length=256, blank=True, null=True)
    twofa = models.CharField(max_length=256, blank=True, null=True)
    uid = models.CharField(max_length=256, blank=True, null=True)
    api_key = models.CharField(max_length=512, blank=True, null=True)
    secret = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        return f'{str(self.user)} - {self.trader}'

    @property
    def get_password(self):
        return decrypt(self.password)

    @property
    def get_twofa(self):
        return decrypt(self.twofa)

    @property
    def get_api_key(self):
        return decrypt(self.api_key)

    @property
    def get_secret(self):
        return decrypt(self.secret)


@receiver(models.signals.pre_save, sender=TraderCredentials)
def encrypt_pw(sender, instance, **kwargs):
    """
    Encrypt plain text password before saving into the db
    """
    if instance.password:
        encrypted = encrypt(instance.password)
        instance.password = encrypted

    if instance.twofa:
        encrypted = encrypt(instance.twofa)
        instance.twofa = encrypted

    if instance.api_key:
        encrypted = encrypt(instance.api_key)
        instance.api_key = encrypted

    if instance.secret:
        encrypted = encrypt(instance.secret)
        instance.secret = encrypted
