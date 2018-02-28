from django.urls import path
from . import views
from blog import settings
from django.conf.urls.static import static

urlpatterns = [
    path('user/CreateAction/', views.api_register, name='api_register'),
    path('user/UserAction/', views.api_login, name='api_login'),
    path('article/<int:article_id>/', views.api_article, name='api_article'),
    path('article/', views.api_create, name='api_create'),
    path('articles/', views.api_list, name='api_list'),
    path('article/<int:article_id>/comment/', views.api_comment_to_article, name='api_comment_to_article'),
    path('comment/<int:comment_id>/child_comment/', views.api_comment_to_comment,
         name='api_comment_to_comment'),
    path('user/img/', views.api_upload_user_img, name='api_upload_user_img'),
    path('user/<int:user_id>/img/', views.api_get_user_img_url, name='api_get_user_img_url')
]
