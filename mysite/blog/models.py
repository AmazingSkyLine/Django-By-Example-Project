from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

# Create your models here.


class PublishedManager(models.Manager):
    def get_queryset(self):
        #  super()调用父类的此方法的部分来实现自定义查询方法
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):
    objects = models.Manager()  # 默认的查询管理
    published = PublishedManager()  # 自定义的查询管理
    tags = TaggableManager()  # tag管理器

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')  # slug是一种短标签，用来命名url，url与publish时间有关

    author = models.ForeignKey(User, related_name='blog_posts')  # 一对多 related_name表示反向的关系
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)  # 自动保存当前日期
    updated = models.DateTimeField(auto_now=True)  # 更新数据时自动保存
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return self.title

    def get_absolute_url(self):  # 解析出url， 将参数传到urls模块，生成url，url将参数传给views模块处理
        return reverse('blog:post_detail',  # 指定解析的地址  blog为应用urls的命名空间, post_detail为url的name
                       args=[
                           self.publish.year,
                           self.publish.strftime('%m'),   # strftime()格式化时间, 保证个位数的月份和日期需要带上0来构建URL
                           self.publish.strftime('%d'),
                           self.slug
                       ])


class Comment(models.Model):
    # related_name 命名从相关联的对象反向定位到这个对象的manager post-->comments example: post.comments.all()
    post = models.ForeignKey(Post, related_name='comments')  # 文章和评论的关系是一对多
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)  # 时间为添加的时间
    updated = models.DateTimeField(auto_now=True)  # 时间为添加或修改的时间
    # 是否显示
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created', )  # 按创建时间排序

    def __str__(self):
        return '{} 对 文章《{}》 的评论'.format(self.name, self.post)

	


