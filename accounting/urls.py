from django.urls import path, include

from accounting import views

app_name = 'accounting'

urlpatterns = [
    path('book-disnat/<int:pk>/', views.book_disnat, name="book-disnat"),
    path('book-crypto/<int:pk>/', views.book_crypto, name="book-crypto"),
    # path('upload/<int:pk>/', views.upload, name="book_upload"),
    # path('export/<int:pk>/', views.export, name="book_export"),
]
