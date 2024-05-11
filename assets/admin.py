from django.contrib import admin

from .models import Asset, Ticker

# Register your models here.
admin.site.register(Asset)
admin.site.register(Ticker)
