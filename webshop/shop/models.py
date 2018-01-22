from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=200,
                            db_index=True)
    slug = models.SlugField(max_length=200,
                            db_index=True,
                            unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_rul(self):
        return reverse('shop:product_list_by_category',
                       args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category,
                                 related_name='products', on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d',
                              blank=True)
    description = models.TextField(blank=True)
    # 十进制型 总共位数10 小数位2
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # 正整数型
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    # auto_to_now 创建时自动添加时间
    created = models.DateTimeField(auto_now_add=True)
    # auto_now 创建和修改时自动添加时间
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        # id和slug共同索引，加快查找速率
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                       args=[self.id, self.slug])
