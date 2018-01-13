# 网站地图
from django.contrib.sitemaps import Sitemap
from .models import Post


class PostSitemap(Sitemap):
    # 页面修改频率
    changefreq = 'weekly'
    # 关联性
    priority = 0.9

    # items()返回在这个站点地图中所包含对象的查询集(QuerySet)
    def items(self):
        return Post.published.all()

    # 接受item()返回的每一个对象并返回对象的最后修改时间
    def lastmod(self, obj):
        return obj.publish