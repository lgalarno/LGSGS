from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.shortcuts import reverse

from assets.tasks import send_email

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
    emailed = models.BooleanField(default=False)

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

    def compose_email(self):
        symbol = self.ticker.symbol
        mail_subject = f'Profit margin reached for {symbol}'
        mail_body = f"""
        Dear {self.user.username}, 

        The profit margin was reached for {symbol}.

        You paid {self.paid}$ for {self.quantity} of {symbol}. With a current value of {self.value}$, the goal 
        of reaching {self.margin}$ profit is achieved and you cand exchange your {symbol}!

        Enjoy your money, and have a good day.

        This email was sent by LGSGS.
        """
        send_email.delay(to_email=self.user.email, mail_subject=mail_subject, mail_body=mail_body)

    # def save(self, *args, **kwargs):
    #     '''
    #     On save, calculate paid
    #     '''
    #     self.paid = round(self.quantity * float(self.price), 2)
    #     super(Asset, self).save(*args, **kwargs)


@receiver(pre_save, sender=Asset)
def target_reached(sender, instance, *args, **kwargs):
    calc_paid = False
    if instance.pk is None:
        calc_paid = True
    else:
        old = Asset.objects.get(id=instance.pk)
        if (instance.quantity != old.quantity) or (instance.price != old.price):
            calc_paid = True
    if calc_paid:
        instance.paid = round(instance.quantity * float(instance.price), 2)


@receiver(post_save, sender=Asset)
def target_reached(sender, instance, created, *args, **kwargs):
    if instance.target_reached and not instance.emailed:
        instance.compose_email()
        instance.emailed = True
        instance.save()