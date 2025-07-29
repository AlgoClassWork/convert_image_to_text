from django.urls import path
from . import views

urlpatterns = [
    # Главная страница для загрузки
    path('', views.upload_image, name='upload_image'),
    # Страница с результатом, принимающая ID объекта
    path('result/<int:pk>/', views.show_result, name='result'),
]