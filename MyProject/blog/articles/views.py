import redis
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from taggit.models import Tag

from blog import settings
from .forms import ArticleEditForm
from .models import Article
from .models import Comment

redis_r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


def article_list(request, tag_id=None):
    articles = Article.objects.filter(status='publish')
    tag = None
    if tag_id:
        tag = get_object_or_404(Tag, id=tag_id)
        articles = articles.filter(tags__in=[tag])
    paginator = Paginator(articles, 5)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    # 请求的页面超出范围
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        articles = paginator.page(paginator.num_pages)

    if request.is_ajax():
        return render(request,
                      'articles/list_ajax.html',
                      {'articles': articles,
                       'tag': tag})
    return render(request,
                  'articles/list.html',
                  {'articles': articles,
                   'tag': tag,
                   'section': 'article'})


def article_detail(request, pk):
    article = get_object_or_404(Article, id=pk)

    total_comments = Comment.objects.filter(article=article, active=True).count()

    # 将成员元素(id)按计数大小倒序排序
    comments_ranking = redis_r.zrange('article_rank', 0, -1, desc=True)[:3]
    # 转化为整型
    article_ids = [int(id) for id in comments_ranking]
    # 获取成员id所对应的文章
    article_rank = list(Article.objects.filter(id__in=article_ids))
    # 将文章按前面排好的成员的位置排序
    article_rank.sort(key=lambda x: article_ids.index(x.id))

    comments = Comment.objects.filter(article=article, active=True)

    return render(request, 'articles/detail.html',
                  {'article': article,
                   'section': 'article',
                   'total_comments': total_comments,
                   'article_rank': article_rank,
                   'comments': comments})


def search(request):
    query = request.GET.get('query')
    articles = None

    if query:
        articles = Article.objects.filter(title__icontains=query)
    return render(request, 'articles/list.html',
                  {'articles': articles,
                   'query': query,
                   })


@login_required
def comment_edit(request, comment_id):
    content = request.GET.get('content')
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.owner:
        return redirect('article_list')

    comment.content = content
    comment.save()

    return redirect('/article/detail/{}/'.format(comment.article.id))


@login_required
def comment_create(request, article_id):
    new_content = request.GET.get('new_content')
    article = get_object_or_404(Article, id=article_id)
    Comment.objects.create(content=new_content, owner=request.user, article=article)
    redis_r.zincrby('article_rank', article.id, amount=1)

    return redirect('/article/detail/{}/'.format(article_id))


@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleEditForm(request.POST)
        if form.is_valid():
            new_article = form.save(commit=False)
            new_article.author = request.user
            new_article.save()
            # save tags
            form.save_m2m()
            return redirect('article_list')
    else:
        form = ArticleEditForm()
    return render(request, 'articles/edit.html', {'form': form})


@login_required
def article_edit(request, article_id):
    # 这里其实使用内置的类视图更方便(UpdateView, CreateView, DeleteView)
    # get返回单个对象，filter返回一个查询组
    article = Article.objects.get(id=article_id)

    if request.user != article.author or request.user.is_superuser == False:
        return redirect('article_list')

    if request.method == 'POST':
        form = ArticleEditForm(instance=article, data=request.POST)
        if form.is_valid():
            update_article = form.save(commit=False)
            update_article.save()
            # 保存多对多对象
            form.save_m2m()
            return redirect('article_list')
    else:
        form = ArticleEditForm(instance=article)
    return render(request, 'articles/edit.html', {'form': form, 'article_id': article_id})


@login_required
def article_delete(request, article_id):
    article = Article.objects.get(id=article_id)

    if request.user == article.author or request.user.is_superuser == True:
        article_title = article.title
        tags = article.tags.all()
        if tags:
            for tag in tags:
                article.tags.remove(str(tag))
        article.delete()
    else:
        return redirect('article_list')

    is_superuser = False
    if request.user.is_superuser:
        is_superuser = True
    return render(request, 'articles/delete_success.html',
                  {'article_title': article_title, 'is_superuser': is_superuser})


def article_manage(request):
    if request.user.is_superuser:
        articles = Article.objects.all()
        return render(request, 'articles/manage.html', {'articles': articles})
    return redirect('article_list')


def comment_manage(request, article_id):
    if request.user.is_superuser:
        article = get_object_or_404(Article, id=article_id)
        comments = Comment.objects.filter(article=article)
        return render(request, 'articles/comment_manage.html', {'comments': comments, 'article': article})
    return redirect('article_list')


def comment_manage_delete(request, comment_id):
    if request.user.is_superuser:
        comment = Comment.objects.get(id=comment_id)
        article = comment.article
        comments = article.comments.all()
        Comment.objects.get(id=comment_id).delete()
        return render(request, 'articles/comment_manage.html', {'comments': comments, 'article': article})
    return redirect('article_list')


def comment_manage_stat(request, comment_id):
    if request.user.is_superuser:
        comment = Comment.objects.get(id=comment_id)
        comment.active = not comment.active
        comment.save()
        article = comment.article
        comments = article.comments.all()
        return render(request, 'articles/comment_manage.html', {'comments': comments, 'article': article})
    return redirect('article_list')
