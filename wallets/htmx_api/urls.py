from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'wallets_htmx-api'

urlpatterns = [
    path('buy/<int:pk>/', login_required(views.buy), name="buy"),
    path('profit/', login_required(views.profit_detail), name="profit"),
    path('sell/<int:pk>/', login_required(views.sell), name="sell"),
    path('transaction/<int:pk>/', login_required(views.transaction_detail), name="transaction"),
    path('transfer/<int:pk>/', login_required(views.transfer), name="transfer"),
    path('wallet-create/', login_required(views.wallet_create), name="wallet_create"),
    path('wallet-detail/<int:pk>/', login_required(views.wallet_detail), name="wallet_detail"),
]
