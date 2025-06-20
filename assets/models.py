from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import reverse

from decimal import Decimal

from assets.tasks import send_email


# Create your models here.


def upload_location(instance, filename):
    # keep for compatibility with migrations
    return f"logos/{filename}"

#
# class Ticker(models.Model):
#     TYPE = (
#         ('crypto', 'Crypto'),
#         ('equity', 'Equity'),
#     )
#     symbol = models.CharField(max_length=16)
#     name = models.CharField(max_length=255, null=True, blank=True)
#     type = models.CharField(max_length=20, choices=TYPE, default=TYPE[0][0])
#
#     def __str__(self):
#         return self.symbol
#
#     def get_absolute_url(self):
#         if self.type == 'equity':
#             url = f"https://ca.finance.yahoo.com/quote/{self.symbol}/"
#         else:
#             url = reverse("assets:detail-ticker", kwargs={"pk": self.pk})
#         return url
#
#
# class Trader(models.Model):
#     FEES = (
#         ('money', 'Money'),
#         ('crypto', 'Crypto'),
#     )
#     name = models.CharField(max_length=255, null=True, blank=True)
#     logo = models.ImageField(upload_to=upload_location,
#                              null=True,
#                              blank=True)
#     url = models.URLField(blank=True, null=True)
#     fees_buy = models.CharField(max_length=20, choices=FEES, default=FEES[0][0])
#     fees_sell = models.CharField(max_length=20, choices=FEES, default=FEES[0][0])
#
#     def __str__(self):
#         return self.name
#
#
# @receiver(models.signals.post_delete, sender=Trader)
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
# @receiver(models.signals.pre_save, sender=Trader)
# def auto_delete_file_on_change(sender, instance, **kwargs):
#     """
#     Deletes old file from filesystem
#     when corresponding `Player` object is updated
#     with new file.
#     """
#     if not instance.pk:
#         return False
#     try:
#         old_logo = Trader.objects.get(pk=instance.pk).logo
#     except Trader.DoesNotExist:
#         return False
#     new_logo = instance.logo
#     if not bool(old_logo):
#         return False
#     if not old_logo == new_logo:
#         if os.path.isfile(old_logo.path):
#             os.remove(old_logo.path)


class Asset(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # ticker = models.ForeignKey(to=Ticker, related_name='asset', on_delete=models.CASCADE)
    # trader = models.ForeignKey(to=Trader, related_name='asset', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    quantity = models.FloatField(validators=[MinValueValidator(0.0)])
    price = models.DecimalField(max_digits=14, decimal_places=6, validators=[MinValueValidator(0.0)])
    fees_per_unit = models.DecimalField(max_digits=14, decimal_places=6, validators=[MinValueValidator(0.0)], default=0)
    current = models.DecimalField(max_digits=14, decimal_places=6, validators=[MinValueValidator(0.0)], default=0)
    margin = models.DecimalField(max_digits=9, decimal_places=2, validators=[MinValueValidator(0.0)], default=0)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    monitor = models.BooleanField(default=True)
    staking = models.BooleanField(default=False)
    emailed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-monitor', 'staking', '-date']

    def __str__(self):
        # return f"{self.transaction.ticker.symbol}-{self.date}"
        return f"{self.id}-{self.date}"

    def get_absolute_url(self):
        return reverse('assets:update-asset', kwargs={'pk': self.pk})

    @property
    def get_delete_url(self):
        return reverse('assets:delete-asset', kwargs={'pk': self.pk})

    @property
    def has_transaction(self):
        return hasattr(self, 'transaction') and self.transaction is not None

    @property
    def target(self):
        return Decimal(self.quantity * float(self.price) + float(self.margin)).quantize(Decimal("1.00"))

    @property
    def target_price(self):
        return Decimal(float(self.target) / self.quantity).quantize(Decimal("1.000000"))

    @property
    def paid(self):
        return Decimal(self.quantity * float(self.price) + self.quantity * float(self.fees_per_unit)).quantize(Decimal("1.00"))

    @property
    def value(self):
        return Decimal(self.quantity * float(self.current)).quantize(Decimal("1.00"))

    @property
    def delta(self):
        return self.value - self.paid  # Decimal(self.value - float(self.paid)).quantize(Decimal("1.00"))

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
        symbol = self.transaction.ticker.symbol
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
        return True


@receiver(post_save, sender=Asset)
def target_reached(sender, instance, created, *args, **kwargs):
    if instance.monitor and not instance.emailed and not created:
        if instance.target_reached:
            instance.compose_email()
            instance.emailed = True
            instance.save()
