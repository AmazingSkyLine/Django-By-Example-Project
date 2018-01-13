from django import template

from ..models import Post  # .返回当前父目录， ..返回当前父目录的上级目录

from django.db.models import Count

from django.utils.safestring import mark_safe
import markdown

register = template.Library()  # 用来注册自定义模板标签和过滤器的实例


@register.simple_tag
# 显示文章总数
def total_posts():  # 默认函数名为tag名，也可以指定装饰器的name属性
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
# 最新的5个帖子
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.assignment_tag
# 评论最多5篇文章
def get_most_commented_posts(count=5):
    # annotate返回以文章评论计数的文章对象列表
    return Post.published.annotate(  # Comment-->post, Post-->comments
        total_comments=Count('comments')).order_by('-total_comments')[:count]


@register.filter(name='markdown')  # 过滤器名字为markdown
# 支持markdown语法
def markdown_format(text):
    return mark_safe(markdown.markdown(text))  # mark_safe()标记结果，使其不被转义为html实体

