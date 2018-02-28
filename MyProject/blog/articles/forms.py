from django import forms

from .models import Comment, Article


class CommentEditForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class ArticleEditForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'tags', 'description', 'content', 'status']

        labels = {
            'title': '标题',
            'tags': '标签',
            'description': '描述',
            'content': '正文',
            'status': '状态'
        }

        help_texts = {
            'tags': '多个标签用逗号分隔'
        }
