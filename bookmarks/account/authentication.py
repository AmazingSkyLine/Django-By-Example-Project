from django.contrib.auth.models import User


class EmailAuthBackend(object):
    # 使用邮箱进行验证
    def authenticate(self, username=None, password=None):
        # 尝试通过阿，email获取对象
        try:
            user = User.objects.get(email=username)
            # 哈希化密码后与数据库中加密密码进行比较
            if user.check_password(password):
                return user
            return None
        except User.DoesNotExist:
            return None

    # 通过id获取用户对象(认证后调用此方法获取用户)
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
