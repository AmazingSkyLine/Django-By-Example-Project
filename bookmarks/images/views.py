from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from actions.utils import create_action
from common.decorators import ajax_required
from .forms import ImageCreateForm
from .models import Image
import redis
from django.conf import settings

# 初始化redis
r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)


@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # form.save()返回一个Image对象
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'bookmarked image', new_item)
            messages.success(request, 'Image added successfully')
            return redirect(new_item.get_absolute_url())
    else:
        form = ImageCreateForm(data=request.GET)
    return render(request, 'images/image/create.html', {'section': 'images',
                                                        'form': form})


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    # incr()--从1开始增加一个键的值,每执行一次增1，返回键的值，开始无键时，默认键值为0
    total_views = r.incr('image:{}:views'.format(image.id))
    # zincrby()命令存储图片视图（views）到一个分类集合中通过键image:ranking。我们存储图片id，和一个分数1，它们将会被加到分类集合中这个元素的总分上。
    r.zincrby('image:ranking', image.id, 1)
    return render(request, 'images/image/detail.html',
                  {'section': 'images',
                   'image': image,
                   'total_views': total_views})


@login_required
@require_POST
@ajax_required
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == "like":
                image.user_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.user_like.remove(request.user)
                create_action(request.user, 'unlikes', image)
            return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'ko'})


def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # 输入非整数，跳转至第一页
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # 空响应停止ajax分页
            return HttpResponse('')
        # 页数超出范围跳转至最后一页
        images = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request,
                      'images/image/list_ajax.html',
                      {'section': 'images', 'images': images})
    return render(request,
                  'images/image/list.html',
                  {'section': 'images', 'images': images})


@login_required
def image_ranking(request):
    # 获取分类集合的所有元素 0最低值 1最高值 倒序
    image_ranking = r.zrange('image:ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    #image_ranking_ids = [id for id in image_ranking]
    # 接下来要使用sort方法，将其转为list
    # 过滤出id在ranking中的
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    # 以id为关键字进行排序
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request,
           'images/image/ranking.html',
           {'section': 'images',
            'most_viewed': most_viewed})
