from django.contrib.auth.models import AbstractUser
from django.db import models
# from django.dispatch import receiver
# from django.db.models import Sum

# from accounts.backend import encrypt_password, decrypt_password
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
# class TraderCredentials(models.Model):
#     user = models.ForeignKey(to=User, on_delete=models.CASCADE)
#     trader = models.ForeignKey(to=TradingPlatform, related_name='credentials', on_delete=models.CASCADE, null=True,
#                                blank=True)
#     unername = models.CharField(max_length=128, blank=True, null=True)
#     password = models.CharField(max_length=128, blank=True, null=True)
#     twofa = models.CharField(max_length=128, blank=True, null=True)
#
#     def __str__(self):
#         return f'{str(self.user)} - {self.trader}'
#
#     def get_password(self):
#         return decrypt_password(self.password)
#
#
# @receiver(models.signals.pre_save, sender=TradingPlatform)
# def encrypt_pw(sender, instance, **kwargs):
#     """
#     Encrypt plain text password before saving into the db
#     """
#     if instance.password:
#         encrypted_password = encrypt_password(instance.password)
#         if encrypted_password:
#             instance.password = encrypted_password
#         else:
#             instance.password = None
