from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserCreatForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')

    password = forms.CharField(max_length=20, label="输入密码",
                               widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=20, label="再次输入密码",
                                widget=forms.PasswordInput)

    cute_name = forms.CharField(label='昵称', max_length=20)

    # clean_的方法在is_valid时检查
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('密码不匹配！')
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']


class ProfileEditFormn(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['cute_name', 'description', 'image']
        labels = {
            'cute_name': '昵称',
            'description': '个人介绍',
            'image': '头像'
        }
