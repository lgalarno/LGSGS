from django.urls import path, include

from assets import views
from .views import AssetUpdateView, AssetDeleteView, AssetDetailView  #, TickerDetailView

app_name = 'assets'

urlpatterns = [
    # path('', AssetListView.as_view(), name="assets"),
    # path('new', views.create_asset, name="create_asset"),
    # path('detail/<int:pk>/', TickerDetailView.as_view(), name="detail-ticker"),
    path('update/<int:pk>/', AssetUpdateView.as_view(), name="update-asset"),
    path('delete/<int:pk>/', AssetDeleteView.as_view(), name="delete-asset"),
]
