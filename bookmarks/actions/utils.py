from django.contrib.contenttypes.models import ContentType
from .models import Action
from django.utils import timezone
import datetime


# 创建用户动作对象的快捷方法
def create_action(user, verb, target=None):
    # 防止用户短时间重复操作
    now = timezone.now()
    # 现在的一分钟前
    last_minute = now - datetime.timedelta(seconds=60)
    # created__gte ==> greater than ? 在现在前一分钟之内的动作
    similar_actions = Action.objects.filter(user_id=user.id, verb=verb, created__gte=last_minute)

    if target:
        target_ct = ContentType.objects.get_for_model(target)
        similar_actions = similar_actions.filter(target_ct=target_ct, target_id=target.id)

    if not similar_actions:
        action = Action(user=user, verb=verb, target=target)
        action.save()
        return True
    return False