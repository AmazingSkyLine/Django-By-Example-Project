from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from actions.models import Action
from actions.utils import create_action
from common.decorators import ajax_required
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile, Contact


# Create your views here.

def user_login(request):
    if request.method == 'POST':
        #  递交表单时
        form = LoginForm(request.POST)
        if form.is_valid():
            # 、表单有效
            cd = form.cleaned_data
            # 用户认证
            user = authenticate(username=cd['username'],
                                password=cd['password'])
            # 若用户名和密码正确，即认证成功
            if user is not None:
                # 若用户未被禁用
                if user.is_active:
                    # 登录，将用户设置到当前对话中
                    login(request, user)
                    return HttpResponse('Authenticated sucessfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                # 认证失败
                return HttpResponse('Invalid login')
    else:
        # 请求页面时
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


# 需要登录
@login_required
def dashboard(request):
    # 展示除了本用户的所有其他用户动作
    actions = Action.objects.exclude(user=request.user)
    # 获取关注用户的id列表
    following_ids = request.user.following.values_list('id', flat=True)
    if following_ids:
        # 如果用户有关注的用户，则显示这些用户的动作
        # select_related()获取与action关联的User对象以及与User关联的Profile对象（针对一对一和一对多）
        # prefetch_related()获取与action关联的target对象（针对GenericForeignKey, 多对多, 多对一）
        actions = actions.filter(user_id__in=following_ids).select_related('user', 'user__profile').prefetch_related(
            'target')
    actions = actions[:10]
    # section用来跟踪用户当前正在查看的页面
    return render(request, 'account/dashboard.html',
                  {'section': 'dashboard',
                   'actions': actions})


# 注册
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # 创建一个新用户对象，但不保存递交
            new_user = user_form.save(commit=False)  # 这里的类型很有趣
            # 给用户添加密码(对密码加密后再保存)
            new_user.set_password(user_form.cleaned_data['password'])
            # 保存对象
            new_user.save()
            # 创建用户资料对象保存至数据库
            profile = Profile.objects.create(user=new_user)
            create_action(new_user, 'has created an account')
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})


@login_required
def edit(request):
    if request.method == 'POST':
        # instance绑定对象到表单，再通过表单模型对数据库进行操作
        user_form = UserEditForm(instance=request.user, data=request.POST)
        # files图片文件  profile字段与user一对一关系
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            # 相当于更新操作
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request, 'account/edit.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'account/user/list.html',
                  {'section': 'people', 'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'account/user/detail.html',
                  {'section': 'people', 'user': user})


@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'ko'})
    return JsonResponse({'status': 'ko'})
