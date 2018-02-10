from django.contrib import admin

from .models import Article, Comment


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'status', 'publish', 'created', 'updated')
    list_filter = ('author', 'title', 'status', 'publish', 'created')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('owner', 'created', 'updated', 'article', 'active')
    list_filter = ('owner', 'created', 'updated', 'article', 'active')


admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment, CommentAdmin)
