import json

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from account.forms import UserCreatForm
from account.models import Profile
from articles.models import Article, Comment
from .jwt_auth import create_token, jwt_auth_user
from .serialize import serialize, error_handle


# Create your views here.


@require_POST
@csrf_exempt
def api_register(request):
    # json格式的数据保存在request.Body里
    form = UserCreatForm(json.loads(request.body))
    if form.is_valid():
        cd = form.cleaned_data
        new_user = User.objects.create(email=cd['email'], username=cd['username'])
        # 设置密码(hash化密码)
        new_user.set_password(cd['password'])
        new_user.save()
        # 创建新的用户资料
        Profile.objects.create(user=new_user,
                               cute_name=cd['cute_name'])

        login(request, new_user)
        # ensure_ascii=False解决中字乱码问题
        data = {'status': 0, 'msg': '注册成功'}
    else:
        data = error_handle('注册失败')
    return JsonResponse(data)


@require_POST
@csrf_exempt
def api_login(request):
    data = json.loads(request.body)
    user = get_object_or_404(User, username=data['username'])
    if user.check_password(data['password']):
        # 创建jwt的token
        jwt_token = create_token(user.username, user.id)
        data = serialize(user, ['id', 'username', 'cute_name', 'is_superuser',
                                'is_active', 'date_joined', 'last_login'], '登录成功')
        data['jwt_token'] = str(jwt_token)[2:-1]
    else:
        data = error_handle('登录失败')
    return JsonResponse(data)


def api_list(request):
    try:
        articles = Article.objects.filter(status='publish')
        data = {}
        i = 1;
        # 构造返回的json数据
        for a in articles:
            article = {}
            article['id'] = a.id
            article['title'] = a.title
            article['author_id'] = a.author.id
            article['publish'] = str(a.publish)
            data[str(i)] = article
            i += 1
        d = {
            'status': 0,
            'msg': "获取文章列表成功",
            'data': data
        }
    except:
        d = error_handle('获取文章列表失败')

    return JsonResponse(d)


def api_detail(request, article_id):
    try:
        article = get_object_or_404(Article, id=article_id)
        data = serialize(article, ['id', 'title', 'tags', 'description', 'content', 'author_id', 'publish'],
                         '获取文章详情成功')
    except:
        data = error_handle('获取文章详情失败')
    return JsonResponse(data)


@csrf_exempt
@require_POST
def api_create(request):
    data = json.loads(request.body)
    jwt_token = request.META.get('HTTP_AUTHORIZATION')
    user = jwt_auth_user(jwt_token)
    if user:
        try:
            # 判断是否提供了status
            if not data.get('status'):
                data['status'] = 'draft'
            new_art = Article.objects.create(title=data['title'], author=user,
                                             description=data['description'], content=data['content'],
                                             status=data['status'])
            if data['tags']:
                for t in data['tags']:
                    new_art.tags.add(t)
            new_art.save()

            data = {'status': 0, 'msg': '文章创建成功'}
        except:
            data = error_handle('文章创建失败')
    else:
        data = error_handle('未登录')
    return JsonResponse(data)


def api_edit(request, article_id):
    try:
        cd = json.loads(request.body)
        article = get_object_or_404(Article, id=article_id)
        jwt_token = request.META.get('HTTP_AUTHORIZATION')
        user = jwt_auth_user(jwt_token)
        if user and (user == article.author or user.is_superuser == True):
            # 判断用户是否拥有权限
            article.title = cd.get('title') or article.title
            article.description = cd.get('description') or article.description
            article.content = cd.get('content') or article.content
            article.status = cd.get('status') or article.status
            if cd.get('tags'):
                tags = article.tags.all()
                if tags:
                    for tag in tags:
                        article.tags.remove(str(tag))
                for t in cd['tags']:
                    article.tags.add(t)
            article.save()
            data = serialize(article, ['id', 'title', 'tags', 'description', 'content'],
                             '文章编辑成功')
        else:
            data = error_handle('文章编辑失败, 当前用户未拥有编辑此文章的权限')
    except:
        data = error_handle('文章编辑失败')
    return JsonResponse(data)


def api_delete(request, article_id):
    cd = json.loads(request.body)
    try:
        article = get_object_or_404(Article, id=article_id)
        jwt_token = request.META.get('HTTP_AUTHORIZATION')
        user = jwt_auth_user(jwt_token)
        if user and (user == article.author or user.is_superuser == True):
            tags = article.tags.all()
            if tags:
                for tag in tags:
                    article.tags.remove(str(tag))
            article.delete()
            data = {'status': 0, 'msg': '文章删除成功'}
        else:
            data = error_handle('文章删除失败, 当前用户未拥有删除此文章的权限')
    except:
        data = error_handle('文章删除失败')
    return JsonResponse(data)


@csrf_exempt
def api_article(request, article_id):
    if request.method == 'GET':
        return api_detail(request, article_id)
    elif request.method == 'PATCH':
        return api_edit(request, article_id)
    elif request.method == 'DELETE':
        return api_delete(request, article_id)
    else:
        return JsonResponse({'status': 1, 'msg': '不合规范的方法!'})


@csrf_exempt
@require_POST
def api_comment_to_article(request, article_id):
    cd = json.loads(request.body)
    jwt_token = request.META.get('HTTP_AUTHORIZATION')
    user = jwt_auth_user(jwt_token)
    if not user:
        return JsonResponse({'status': 1, 'msg': '未登录'})
    article = get_object_or_404(Article, id=article_id)
    if article:
        try:
            new_comment = Comment.objects.create(owner=user, content=cd['content'], article=article)
            data = {'status': 0, 'msg': '评论发表成功！'}
        except:
            data = error_handle('评论发表失败！')
    else:
        data = error_handle('没有找到指定的文章！')
    return JsonResponse(data)


@csrf_exempt
@require_POST
def api_comment_to_comment(request, comment_id):
    cd = json.loads(request.body)
    jwt_token = request.META.get('HTTP_AUTHORIZATION')
    user = jwt_auth_user(jwt_token)
    if not user:
        return JsonResponse({'status': 1, 'msg': '未登录'})
    comment = get_object_or_404(Comment, id=comment_id)
    if comment:
        try:
            new_comment = Comment.objects.create(owner=user, content=cd['content'], article=comment.article,
                                                 parent=comment)
            data = {'status': 0, 'msg': '评论发表成功！'}
        except:
            data = error_handle('评论发表失败！')
    else:
        data = error_handle('没有找到指定的评论！')
    return JsonResponse(data)


def api_upload_user_img(request):
    jwt_token = request.META.get('HTTP_AUTHORIZATION')
    user = jwt_auth_user(jwt_token)
    if not user:
        return JsonResponse({'status': 1, 'msg': '未登录'})
    if request.method == 'POST':
        img = request.FILES.get('img')
        profile = get_object_or_404(Profile, user=user)
        profile.image = img
        profile.save()
        try:
            data = {'status': 0, 'msg': '图片上传成功！'}
        except:
            data = {'status': 1, 'mag': '图片上传失败！'}

        return JsonResponse(data)
    else:
        return render(request, 'img_upload.html')


def api_get_user_img_url(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not user:
        return JsonResponse(error_handle('未找到指定用户！'))
    profile = get_object_or_404(Profile, user=user)
    if not profile:
        return JsonResponse(error_handle('该用户没有资料！'))
    img_url = '/' + request.META['HTTP_HOST'] + profile.image.url
    if not img_url:
        return JsonResponse(error_handle('该用户没有头像！'))
    return JsonResponse({'status': 0, 'msg': "获取用户头像成功！", "data": {
        "img_url": img_url
    }})
