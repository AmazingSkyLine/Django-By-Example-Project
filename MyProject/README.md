# README

---

基于Django的简单博客API，实现了文章的CURD，用户的登录及注册，对文章和评论的评论功能。
使用JWT进行验证，访问需要登录的页面时，在HTTP头的Authorization添加token信息进行认证。
创建评论或文章所需数据使用json格式传送，获取或删除具体页面通过query_string传送数据。

**RESTful API的命名规范**
> RESTful API的URL以资源来命名，通过不同的HTTP请求方式来表现不同操作，不将具体操作暴露在URL中。
```
GET: 获取资源
POST: 新建资源
PUT: 替换资源
PATCH: 更新资源
DELETE: 删除资源
```

API文档地址：http://showdoc.fenlan96.com/index.php?s=/8&amp;page_id=29

**参考资料**
> RESTful API的文章  [csdn](http://www.csdn.net/article/2013-06-13/2815744-RESTful-API)



