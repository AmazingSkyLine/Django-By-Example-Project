from django.urls import path

from . import views

urlpatterns = [
    path('tag/<slug:tag_id>/', views.article_list, name='article_list_by_tag'),
    path('detail/<int:pk>/', views.article_detail, name='article_detail'),
    path('search/', views.search, name='search'),
    path('comment_edit/<int:comment_id>', views.comment_edit, name='comment_edit'),
    path('comment_create/<int:article_id>', views.comment_create, name='comment_create'),
    path('manage/create/', views.article_create, name='article_create'),
    path('manage/edit/<int:article_id>', views.article_edit, name='article_edit'),
    path('manage/delete/<int:article_id>', views.article_delete, name='article_delete'),
    path('manage/', views.article_manage, name='article_manage'),
]
