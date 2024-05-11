from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'assets_htmx-api'

urlpatterns = [
    path('ticker-create/', login_required(views.ticker_create), name="ticker_create"),
    path('ticker-list/', login_required(views.ticker_list), name="ticker-list"),
    # path('ticker-validate/', login_required(views.ticker_validate), name="ticker_validate"),
]
