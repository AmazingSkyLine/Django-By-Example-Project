from django import forms
from courses.models import Course

# 学生选课表单，在课程详情页设置一个按钮，按下提交表单，所有此表单可以隐藏
class CourseEnrollForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all(),
                                    widget=forms.HiddenInput)