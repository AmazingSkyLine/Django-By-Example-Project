from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse

# Create your models here.


class Image(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.DO_NOTHING,
                             related_name='images_created')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    url = models.URLField()
    image = models.ImageField(upload_to='image/%Y/%m/%d')
    description = models.TextField(blank=True)
    # 创建数据库索引
    created = models.DateField(auto_now_add=True, db_index=True)

    # 多对多关系
    user_like = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       related_name='images_liked',
                                       blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # 调用父类的save()方法，相当与对类的save()进行部分重写，剩下的继承父类方法
        super(Image, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('images:detail', args=(self.id, self.slug))

