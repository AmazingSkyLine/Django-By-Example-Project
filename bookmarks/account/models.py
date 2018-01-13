from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    # profile与user一一对应
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)   # 这里并没有直接调用auth的User模型
    date_of_birth = models.DateField(blank=True, null=True)  # 允许不填或为无
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)


# 用户关系
class Contact(models.Model):
    user_from = models.ForeignKey(User, related_name='rel_from_set', on_delete=models.DO_NOTHING)
    user_to = models.ForeignKey(User, related_name='rel_to_set', on_delete=models.DO_NOTHING)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created', )

    def __str__(self):
        return '{} follows {}'.format(self.user_from, self.user_to)

# 动态地给User模型添加字段
User.add_to_class('following',
                  models.ManyToManyField(
                      'self',
                      through=Contact,
                      related_name='followers',
                      symmetrical=False  # 非对称
                  ))