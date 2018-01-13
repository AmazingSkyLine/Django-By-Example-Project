from django import forms

from .models import Comment


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    # require 是否必需
    comments = forms.CharField(required=False, widget=forms.Textarea)


# 根据模型创建表单
class CommentForm(forms.ModelForm):
    class Meta:
        # 所使用的模型
        model = Comment
        # 表单的域
        fields = ('name', 'email', 'body')