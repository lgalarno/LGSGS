from django.urls import path, include

from accounting import views

app_name = 'accounting'

urlpatterns = [
    path('book-disnat/<int:pk>/', views.book_disnat, name="book-disnat"),
    path('book-crypto/<int:pk>/', views.book_crypto, name="book-crypto"),
    path('crypto-for-taxes/<int:pk>/', views.crypto_for_taxes_view, name="crypto-for-taxes"),
    path('upload/<int:pk>/', views.upload, name="upload"),
]
