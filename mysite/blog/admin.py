from django.contrib import admin

from .models import Post, Comment

# Register your models here.


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')  # 显示的属性
    list_filter = ('status', 'created', 'publish', 'author')  # 可以通过这些来筛选
    search_fields = ('title', 'body')  # 搜索方向
    prepopulated_fields = {'slug': ('title', )}  # 预填充
    raw_id_fields = ('author', )  # 使author字段显示为一个搜索框，而非下拉框
    date_hierarchy = 'publish'  # 通过时间层快速导航
    ordering = ['status', 'publish']  # 排序


class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)