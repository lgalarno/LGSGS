from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum

# Create your models here.


class User(AbstractUser):
    website = models.URLField(blank=True, verbose_name='External portfolio url')
    country = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return self.username

    def total_balance(self):
        wallets = self.wallet_set.all()
        return wallets.aggregate(Sum('balance', default=0))['balance__sum']
