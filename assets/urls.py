from django.urls import path, include

from assets import views
from .views import AssetListView, AssetUpdateView, AssetDeleteView, AssetDetailView

app_name = 'assets'

urlpatterns = [
    path('', AssetListView.as_view(), name="assets"),
    path('new', views.create_asset, name="create_asset"),
    path('detail/<int:pk>/', AssetDetailView.as_view(), name="detail-asset"),
    path('update/<int:pk>/', AssetUpdateView.as_view(), name="update-asset"),
    path('delete/<int:pk>/', AssetDeleteView.as_view(), name="delete-asset"),
    path('htmx-api/', include('assets.htmx_api.urls', namespace="assets-htmx-api")),
]
