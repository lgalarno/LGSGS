from django.contrib import admin

from .models import Wallet, Transfer, Transaction, Profit

# Register your models here.
admin.site.register(Wallet)
admin.site.register(Transfer)
admin.site.register(Transaction)
admin.site.register(Profit)
