from django.urls import path, include


app_name = 'wallets'

urlpatterns = [
    path('htmx-api/', include('wallets.htmx_api.urls', namespace="wallets-htmx-api")),
]
