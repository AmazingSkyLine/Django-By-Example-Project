from django import forms
from django.forms.models import inlineformset_factory
from .models import Course, Module

# formset一页显示多个表单
# extra设置每次显示空的额外表单数
# can_delete给所有表单渲染一个复选框，允许你确认这个对象你真的要删除
ModuleFormSet = inlineformset_factory(Course,
                                      Module,
                                      fields=['title', 'description'],
                                      extra=2,
                                      can_delete=True)