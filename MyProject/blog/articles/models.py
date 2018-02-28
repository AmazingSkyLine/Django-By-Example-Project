from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager

STATUS_CHOICES = [('Draft', 'draft'),
                  ('Publish', 'publish')]


class Article(models.Model):
    tags = TaggableManager()
    author = models.ForeignKey(User, related_name='articles',
                               on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    content = RichTextUploadingField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,
                              default='draft')
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    owner = models.ForeignKey(User, related_name='comments',
                              on_delete=models.CASCADE)

    article = models.ForeignKey(Article, related_name='comments',
                                on_delete=models.CASCADE)

    # 父评论
    parent = models.ForeignKey('Comment', null=True, blank=True, related_name='reply_comments',
                               on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    content = models.TextField()
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('-updated',)

    def __str__(self):
        return 'Comment By' + self.owner.profile.cute_name + 'to article:' + self.article.title
