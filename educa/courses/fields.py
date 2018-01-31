from django.db import models
from django.core.exceptions import ObjectDoesNotExist


# 定制字段
# 实现功能：
# 自动分配一个次序值当没有指定次序被提供时，当没有次数被提供时，自动分配下一个次序
# 值为最近的次序加1，若无最近的次序，则值为0
# 次序与其他字段有关。例如课程模块将按照它们所属的课程和相关模块的内容进行排序
class OrderField(models.PositiveIntegerField):

    # for_fields参数为与排序相关的字段
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        # 调用父类的__init__()
        super(OrderField, self).__init__(*args, **kwargs)

    # 字段被保存之前调用此方法
    def pre_save(self, model_instance, add):
        # 如果含有此字段的实例对象的此字段的值为None
        if getattr(model_instance, self.attname) is None:
            try:
                # 此字段所对应的模型所含的所有对象
                qs = self.model.objects.all()
                # 如果有与排序相关的字段
                if self.for_fields:
                    # 获取实例对象的相关字段的值{field： value}
                    query = {field: getattr(model_instance, field) for field in self.for_fields}
                    # 过滤出和此对象含有相关字段值相同的对象
                    qs = qs.filter(**query)
                    # 获取最近一个对象的value
                    last_item = qs.latest(self.attname)
                    value = last_item.order + 1
            except ObjectDoesNotExist:
                # 如果最近无对象，则value为0
                value = 0
            # 设置字段的值
            setattr(model_instance, self.attname, value)
            return value
        else:
            # 如果对象此字段有值，调用父类方法，什么也不做
            return super(OrderField, self).pre_save(model_instance, add)
