from django import forms
from django.contrib.auth.models import User

from .models import Profile


# 登录表单
class LoginForm(forms.Form):
    username = forms.CharField(label="用户名")
    password = forms.CharField(label="密码", widget=forms.PasswordInput)


# 注册表单
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label="输入密码", widget=forms.PasswordInput)
    password2 = forms.CharField(label="再次输入密码", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name')

    def clean_password2(self):
        cd = self.cleaned_data  # 表单数据
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('密码不匹配!')
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'email')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('date_of_birth', 'photo')
