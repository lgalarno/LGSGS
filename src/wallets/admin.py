from django.contrib import admin

from .models import Wallet, Transaction, Profit, TradingPlatform, Ticker  # , Transfer

# Register your models here.
admin.site.register(Wallet)
# admin.site.register(Transfer)
admin.site.register(Transaction)
admin.site.register(Profit)
admin.site.register(TradingPlatform)
admin.site.register(Ticker)
