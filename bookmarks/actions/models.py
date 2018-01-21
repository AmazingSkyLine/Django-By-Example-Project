from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


# 用户动作记录
class Action(models.Model):
    user = models.ForeignKey(User, related_name='actions', db_index=True, on_delete=models.DO_NOTHING)
    # 操作
    verb = models.CharField(max_length=255)
    # 目标模型
    target_ct = models.ForeignKey(ContentType, blank=True, null=True, related_name='target_obj',
                                  on_delete=models.DO_NOTHING)
    # 目标主键
    target_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    # 目标
    target = GenericForeignKey('target_ct', 'target_id')
    # 操作时间
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created',)
