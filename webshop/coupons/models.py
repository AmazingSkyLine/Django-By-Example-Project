from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# 优惠券
class Coupon(models.Model):
    # 代码 无重复
    code = models.CharField(max_length=50, unique=True)
    # 有效时间
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    # 折扣 validator限制最值
    discount = models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(100)])

    active = models.BooleanField()

    def __str__(self):
        return self.code
