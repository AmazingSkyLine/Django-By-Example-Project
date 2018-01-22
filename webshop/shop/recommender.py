import redis
from django.conf import settings
from .models import Product

r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)

class Recommender(object):

    # 获取某个商品对应的redis键
    def get_product_key(self, id):
        return 'product:{}:purchased_with'.format(id)

    def product_bought(self, products):
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                # 获取和某个商品一起买的其他所有商品
                if with_id != product_id:
                    # 某个商品键，其成员为和其一起买的其他商品
                    # 每访问一次其他商品，那个商品的计数加1
                    # example:
                    # product:33:purchased_with:{
                    #   22: 1
                    #   44: 1
                    #   55: 1
                    #   with_id: amount
                    r.zincrby(self.get_product_key(product_id),
                              with_id,
                              amount=1)

    def suggest_products_for(self, products, max_result=6):
        product_ids = [p.id for p in products]
        if len(products) == 1:
            # 如果只有一个产品
            # 0最小值 -1最大值 倒序 选取键中成员
            suggestions = r.zrange(
                self.get_product_key(product_ids[0]),
            0, -1, desc=True)[:max_result]

        else:
            # 如果产品不为1
            # 将所有键拼接成一个键
            flat_ids = ''.join([str(id) for id in product_ids])
            tmp_key = 'tmp_{}'.format(flat_ids)
            # 获取所有购物单上产品的键
            keys = [self.get_product_key(id) for id in product_ids]
            # 累加所有键的结果
            # example
            #   product_ids = [1, 2, 3]
            #   flat_ids = 123
            #   tmp_key = tmp_123
            #   keys = [1, 2, 3]  简写了key
            #   1:{3(1), 4(2), 5(3)}
            #   2:{3(1), 4(2), 5(3)}
            #   3:{1(1), 4(2), 5(3)}
            #   --zunionstore()后--
            #   tmp_key:{1(1), 3(2), 4(6), 5(9)}
            #   --zrem()后--
            #   tmp_key:{4(6), 5(9)}
            r.zunionstore(tmp_key, keys)
            # 删除和购物单产品重复的
            r.zrem(tmp_key, *product_ids)
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_result]
            # 删除临时键
            r.delete(tmp_key)

        suggested_products_ids = [int(id) for id in suggestions]

        # 获取建议的对象，并按出现顺序排序
        # index返回对象的索引位置
        suggested_products = list(Product.objects.filter(id__in=suggested_products_ids))
        suggested_products.sort(key=lambda x: suggested_products_ids.index(x.id))
        return suggested_products

    # 删除所有推荐
    def clear_purchases(self):
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))