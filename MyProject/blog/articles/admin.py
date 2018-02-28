from django.contrib import admin

from .models import Article, Comment


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'status', 'publish', 'created', 'updated')
    list_filter = ('author', 'title', 'status', 'publish', 'created')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('owner', 'created', 'updated', 'active', 'article', 'parent')
    list_filter = ('owner', 'created', 'updated', 'active', 'article', 'parent')


admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment, CommentAdmin)
