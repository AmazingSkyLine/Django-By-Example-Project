# README

---

基于Django的简单博客API，只实现了文章的CURD和用户的登录及注册。

**RESTful API的命名规范**
> RESTful API的URL以资源来命名，通过不同的HTTP请求方式来表现不同操作，不将具体操作暴露在URL中。
```
GET: 获取资源
POST: 新建资源
PUT: 替换资源
PATCH: 更新资源
DELETE: 删除资源
```

由于做的时候有点智障，请求是用json传参数的，而不是key-value对，有点麻烦。

API文档地址：http://showdoc.fenlan96.com/index.php?s=/8

**参考资料**
> RESTful API的文章  [csdn](http://www.csdn.net/article/2013-06-13/2815744-RESTful-API)



