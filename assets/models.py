from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.shortcuts import reverse

from assets.backend import current_price

# Create your models here.


class Ticker(models.Model):
    symbol = models.CharField(max_length=16)
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.symbol


class Asset(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ticker = models.ForeignKey(to=Ticker, related_name='ticker', on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    quantity = models.FloatField(validators=[MinValueValidator(0.0)])
    price = models.DecimalField(max_digits=14, decimal_places=6, validators=[MinValueValidator(0.0)])
    current = models.DecimalField(max_digits=14, decimal_places=6, validators=[MinValueValidator(0.0)], default=0)
    paid = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    margin = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(0.0)], default=0)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    monitor = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.ticker.symbol}"

    @property
    def get_absolute_url(self):
        return reverse('assets:detail-asset', kwargs={'pk': self.pk})

    @property
    def get_update_url(self):
        return reverse('assets:update-asset', kwargs={'pk': self.pk})

    @property
    def get_delete_url(self):
        return reverse('assets:delete-asset', kwargs={'pk': self.pk})

    @property
    def target(self):
        return round(self.paid + self.margin, 2)

    @property
    def value(self):
        return round(self.quantity * float(self.current), 2)

    @property
    def delta(self):
        return round(self.value - float(self.paid), 2)

    @property
    def target_reached(self):
        return self.delta > self.margin

    @property
    def target_reached(self):
        return self.delta > self.margin

    @property
    def delta_alert(self):
        if self.target_reached:
            a = 'alert-success'
        elif self.value < self.paid:
            a = 'alert-danger'
        else:
            a = 'alert-primary'
        return a

    def save(self, *args, **kwargs):
        '''
        On save, calculate paid
        '''
        self.paid = round(self.quantity * float(self.price), 2)
        self.current = current_price(self.ticker.symbol)
        super(Asset, self).save(*args, **kwargs)
