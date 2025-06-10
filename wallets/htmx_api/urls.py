from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'wallets_htmx-api'

urlpatterns = [
    path('buy/<int:pk>/', login_required(views.buy), name="buy"),
    path('profit/<int:pk>/', login_required(views.profit_detail), name="profit"),
    path('update/', login_required(views.update), name="update"),
    path('trading-platform-create/', login_required(views.trading_platform_create), name="trading_platform_create"),
    path('trading-platform-list/', login_required(views.trading_platform_list), name="trading-platform-list"),
    path('ticker-create/', login_required(views.ticker_create), name="ticker_create"),
    path('ticker-list/<int:pk>/', login_required(views.ticker_list), name="ticker-list"),
    path('profit-list/<int:pk>/', login_required(views.profit_list), name="profit-list"),
    path('sell/<int:pk>/', login_required(views.sell), name="sell"),
    path('transaction/<int:pk>/', login_required(views.transaction_detail), name="transaction"),
    path('transaction-list/<int:pk>/', login_required(views.transaction_list), name="transaction-list"),
    path('asset-list /<int:pk>/', login_required(views.asset_list), name="asset-list"),
   path('transfer/<int:pk>/', login_required(views.transfer), name="transfer"),
#    path('transfer-list/<int:pk>/', login_required(views.transfer_list), name="transfer-list"),
    path('wallet-create/', login_required(views.wallet_create), name="wallet_create"),
    path('wallet-update/<int:pk>/', login_required(views.wallet_update), name="wallet_update"),
    path('wallet-detail/<int:pk>/', login_required(views.wallet_detail), name="wallet_detail"),
]
