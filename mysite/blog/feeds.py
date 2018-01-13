# Feed，与RSS(聚合内容)有关，是一种信息的摘要
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from .models import Post


class LatestPostsFeed(Feed):
    title = '博客'
    link = '/blog/'
    description = '新文章'

    # items()返回在这个Feed中所包含对象的查询集(QuerySet)
    def items(self):
        return Post.published.all()[:5]

    # 接受item()返回的每一个对象并返回对象的标题
    def item_tite(self, item):
        return item.title

    # 接受item()返回的每一个对象并返回对象的描述
    def item_description(self, item):
        return truncatewords(item.body, 30)