from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CourseEnrollForm
from django.views.generic.list import ListView
from courses.models import Course
from django.views.generic.detail import DetailView

class StudentRegistrationView(CreateView):
    template_name = 'students/student/registration.html'
    # 用于创建对象的表单
    form_class = UserCreationForm
    success_url = reverse_lazy('student_course_list')

    # 覆写form_valid()方法，使用户成功注册后直接登录
    def form_valid(self, form):
        result = super(StudentRegistrationView, self).form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'],
                            password=cd['password'])
        login(self.request, user)
        return result

class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super(StudentEnrollCourseView, self).form_valid(form)

    # 相当于success_url属性
    def get_success_url(self):
        return reverse_lazy('student_course_detail',
                            args=[self.course.id])

class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'

    # 检索出当前用户报名了的课程
    def get_queryset(self):
        qs = super(StudentCourseListView, self).get_queryset()
        return qs.filter(students__in=[self.request.user])

class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        qs = super(StudentCourseDetailView, self).get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super(StudentCourseDetailView, self).get_context_data(**kwargs)
        # 获取课程对象
        course = self.get_object()
        # 如果给了url参数module_id, 获取那个模块，否则获取第一个模块
        if 'module_id' in self.kwargs:
            # 获取当前模块
            context['module'] = course.modules.get(id=self.kwargs['module_id'])
        else:
            # 如果课程拥有的模块非空
            if course.modules.all():
                # 获取第一个模块
                context['module'] = course.modules.all()[0]
        return context