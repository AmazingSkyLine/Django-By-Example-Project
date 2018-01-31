from django import template

register = template.Library()

@register.filter
def model_name(obj):
    try:
        # 可以从对象的Meta类中获取对象的模型名
        return obj._meta.model_name
    except AttributeError:
        return None