from django.urls import path, include

from wallets import views
from wallets.views import WalletDeleteView

app_name = 'wallets'

urlpatterns = [
    path('', views.wallets, name="wallets"),
    path('delete-wallet/<int:pk>/', WalletDeleteView.as_view(), name="delete-wallets"),
    path('htmx-api/', include('wallets.htmx_api.urls', namespace="wallets-htmx-api")),
]
