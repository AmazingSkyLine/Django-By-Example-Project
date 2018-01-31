from braces.views import CsrfExemptMixin, JSONRequestResponseMixin
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count
from django.forms.models import modelform_factory
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .forms import ModuleFormSet
from .models import Course, Module, Content, Subject

from students.forms import CourseEnrollForm

'''
# 课程管理视图类
class ManageCourseListView(ListView):
    model = Course
    template_name = 'courses/manage/course/list.html'

    # 重写检索方法
    # 只显示登录者为拥有者的课程
    def get_queryset(self):
        qs = super(ManageCourseListView, self).get_queryset()
        return qs.filter(owner=self.request.user)
'''


class OwnerMixin(object):
    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    # 这个方法默认的行为是保存实例（对于模型表单）以及重定向用户到success_url
    # 重写表单的验证方法
    # 当表单有效时，将对象的拥有者设为当前用户
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin):
    model = Course


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    fields = ['subject', 'title', 'slug', 'overview']
    template_name = 'courses/manage/course/form.html'
    success_url = reverse_lazy('manage_course_list')


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'


class CourseCreateView(PermissionRequiredMixin, OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'


class CourseUpdateView(PermissionRequiredMixin, OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'


class CourseDeleteView(PermissionRequiredMixin, OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    success_url = reverse_lazy('manage_course_list')
    permission_required = 'courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    # 获取ModuleFormSet
    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    # 分配http请求(get/post)
    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super(CourseModuleUpdateView, self).dispatch(request, pk)

    # 处理get请求
    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,
                                        'formset': formset})

    # 处理post请求
    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        # 表单有效，保存至数据库，跳转至课程列表页，否则留着原页面
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course,
                                        'formset': formset})


# View基于类的视图
# TemplateResponseMixin负责渲染模板及返回一个http响应
# 需要template_name属性，提供一个render_to_response()方法
# 通用内容类
class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    # 获取对应的内容模型
    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    # 构造modelForm
    def get_form(self, model, *args, **kwargs):
        # 表单域为去除几个类型都有的公共域外的其他域
        Form = modelform_factory(model, exclude=['owner',
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)

    # 分配http请求
    def dispatch(self, request, module_id, model_name, id=None):
        # 获取与当前内容有关的module对象
        self.module = get_object_or_404(Module, id=module_id,
                                        course__owner=request.user)
        # 获取内容类型
        self.model = self.get_model(model_name)
        if id:
            # 获取内容类型的具体对象
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         owner=request.user)
        return super(ContentCreateUpdateView, self).dispatch(request,
                                                             module_id,
                                                             model_name,
                                                             id)

    def get(self, request, module_id, model_id, model_name, id=None):
        # 新建内容时，传入model, obj为None
        # 编辑内容时，传入model和obj
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
                                        'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # 新建内容
                Content.objects.create(module=self.module,
                                       item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form,
                                        'object': self.obj})


class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    module__course__owner=request.user)
        module = content.module
        # 删除content对应的具体类型
        content.item.delete()
        # 删除content
        content.delete()
        return redirect('module_content_list', module.id)


# 内容列表类
class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                   id=module_id,
                                   course__owner=request.user)
        return self.render_to_response({'module': module})


# 模块排序类
class ModuleOrderView(CsrfExemptMixin, JSONRequestResponseMixin, View):
    # CsrfExemptMixin 避免csrf标签检查
    # JSONRequestResponseMixin 将请求的数据JSON化，返回一个json格式的http响应
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id, course__owner=request.user).update(order=order)
        return self.render_json_response({'save': 'ok'})


class ContentOrderView(CsrfExemptMixin, JSONRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,
                                   module__course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


# 课程显示类
class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        # 科目包含的课程总数
        subjects = Subject.objects.annotate(
            total_courses=Count('courses'))
        courses = Course.objects.annotate(
            total_modules=Count('modules'))

        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            courses = courses.filter(subject=subject)

        return self.render_to_response({'subjects': subjects,
                                        'courses': courses,
                                        'subject': subject})


class CourseDetailView(DetailView):
    # DetailView期望一个主键(pk)或者slug来检索对应模型的单一对象
    model = Course
    template_name = 'courses/course/detail.html'

    # 在渲染进模板的上下文里引入报名表
    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(
            initial={'course': self.object})
        return context
