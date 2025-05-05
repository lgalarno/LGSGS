from django.urls import path, include

from accounting import views

app_name = 'accounting'

urlpatterns = [
    path('book/<int:pk>/', views.book, name="book"),
    # path('upload/<int:pk>/', views.upload, name="book_upload"),
    # path('export/<int:pk>/', views.export, name="book_export"),
]
