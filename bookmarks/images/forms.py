from django import forms
from .models import Image
from urllib import request
from django.core.files.base import ContentFile
from django.utils.text import slugify


# 图片上传表单
class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'url', 'description']
        widgets = {
            'url': forms.HiddenInput,
        }

    # 判断url是否合法
    def clean_url(self):
        url = self.cleaned_data['url']
        valid_extensions = ['jpg', 'jpeg']
        # 以右边第一个点为分界线，分为两个字符串，返回一个list，取后面那个，即图片的格式
        extension = url.rsplit('.', 1)[1].lower()
        if extension not in valid_extensions:
            raise forms.ValidationError('The given URL does not match valid image extensions.')
        return url

    def save(self, force_insert=False, force_update=False, commit=True):
        # 调用父类save()方法返回对象实例但暂时不递交至数据库
        image = super(ImageCreateForm, self).save(commit=False)
        image_url = self.cleaned_data['url']
        # 图片名称
        image_name = '{}.{}'.format(slugify(image.title),
                                    image_url.rsplit('.', 1)[1].lower())
        # 下载图片
        response = request.urlopen(image_url)
        # 调用save()方法把图片传递给ContentFile对象，这个对象被下载的文件所实例化
        # Image模型的image字段保存将其保存，但暂时不递交至数据库
        image.image.save(image_name, ContentFile(response.read()), save=False)

        if commit:
            image.save()
        return image

