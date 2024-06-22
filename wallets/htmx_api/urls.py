from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'wallets_htmx-api'

urlpatterns = [
    path('wallet-create/', login_required(views.wallet_create), name="wallet_create"),
]

