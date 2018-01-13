from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail

from .models import Post

from taggit.models import Tag

from django.db.models import Count  # 聚合函数

# Create your views here.


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'  # 传递给模板的字典的key
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_list(request, tag_slug=None):
    object_list = Post.published.order_by('-publish')  # 按发表时间降序返回所有文章
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)  # 用给定的slug获取标签对象
        object_list = object_list.filter(tags__in=[tag])  # 包含给定标签的文章

    paginator = Paginator(object_list, 3)  # 一页显示3个
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:  # 如果页数不是整数，跳到第一页
        posts = paginator.page(1)
    except EmptyPage:  # 页数超出范围，跳到最后一页
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts,
                   'page': page,
                   'tag': tag})


def post_detail(request, year, month, day, post):
    # 从Post表中取出符合条件的数据，若没有则显示404
    post = get_object_or_404(Post,
                             slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)  # 这里为双杠，表示访问字段的分量
    # 所有可显示的列表
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        # 评论表单被递交
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # 创建评论对象，但不提交至数据库
            new_comment = comment_form.save(commit=False)
            # 关联目前的文章到评论对象
            new_comment.post = post
            # 保存评论到数据库
            new_comment.save()
    else:
        comment_form = CommentForm()

    # 列出相似文章
    # 本文所有tag的id, 以简单列表形式
    post_tags_ids = post.tags.values_list('id', flat=True)
    # 除本文外其他tag的id相同的文章
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
        .exclude(id=post.id)
    # 含指定标签的文章（除了本文）  annotate返回所有含此标签的文章  Count记录相同的标签数
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
        .order_by('-same_tags', '-publish')[:4]  # 以相同标签数降序排列，显示4个

    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form,
                   'similar_posts': similar_posts})


def post_share(request, post_id):
    # 通过id获取指定文章
    post = get_object_or_404(Post, id=post_id, status='published')
    cd = None
    if request.method == 'POST':
        # 表单被提交
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # 表单数据有效
            cd = form.cleaned_data
            # 构建url完全路径
            post_url = request.build_absolute_uri(post.get_absolute_url())
            # 邮件标题
            subject = '{}({}) 推荐你阅读 "{}" '.format(cd['name'], cd['email'], post.title)
            # 邮件主体
            message = '查看 "{}" 来自 {}\n\n{}的评论: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            # 发送邮件
            send_mail(subject, message, '1546056871@qq.com', [cd['to']])
            # sent判断是否已经发送邮件及邮件是否发送成功，未发邮件或是发送出错sent都不为True
            sent = True
    else:
        # GET获取页面, 显示空表单
        form = EmailPostForm()
    return render(request, 'blog/post/share.html',
                  {'post': post,
                   'form': form,
                   'cd': cd})
