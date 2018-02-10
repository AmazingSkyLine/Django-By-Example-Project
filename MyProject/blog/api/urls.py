from django.urls import path
from . import views

urlpatterns = [
    path('user/CreateAction/', views.api_register, name='api_register'),
    path('user/UserAction/', views.api_login, name='api_login'),
    path('article/', views.api_article, name='api_article'),
    path('articles/', views.api_list, name='api_list'),
]
