from django.conf import settings
from django.db import models

# Create your models here.


# class Wallet(models.Model):
#     user = models.ForeignKey(to=User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=120, blank=True, null=True)
#     balance = models.DecimalField(max_digits=10, decimal_places=2)
#
#     def __str__(self):
#         return f"{str(self.user)}-{self.name}"  # str(self.user)
#
#
# class Transfer(models.Model):
#     TYPE = (
#         ('deposit', 'Deposit'),
#         ('withdrawal', 'Withdrawal'),
#     )
#     wallet = models.ForeignKey(to=Wallet, on_delete=models.CASCADE)
#     type = models.CharField(max_length=20, choices=TYPE)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     date = models.DateField()
#
#     def __str__(self):
#         return f"{str(self.wallet.name)}-{str(self.amount)}$"
