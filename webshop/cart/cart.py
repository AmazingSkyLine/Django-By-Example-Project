from decimal import Decimal

from django.conf import settings

from shop.models import Product

from coupons.models import Coupon


class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # 保存一个空购物车至会话
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        self.coupon_id = self.session.get('coupon_id')

    def add(self, product, quantity=1, update_quantity=False):
        # 添加一个产品至购物车或者更新其数量
        # json格式的会话，json里键值类型为str
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}

        if update_quantity:
            # 直接更新数量
            self.cart[product_id]['quantity'] = quantity
        else:
            # 一个一个添加
            self.cart[product_id]['quantity'] += 1

        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        # 标记会话为modified来确保它被保存了
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    # 迭代时执行
    def __iter__(self):
        # 迭代购物车中的物品
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            # 为每个购物车的数据添加product
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            # 将str再转回十进制
            item['price'] = Decimal(item['price'])
            # 计算总价
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        # 计算购物车商品总数
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        # 计算购物车总价
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # 清空购物车
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    # 可以以属性字段的方式访问此方法
    @property
    def coupon(self):
        if self.coupon_id:
            return Coupon.objects.get(id=self.coupon_id)
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal('100')) * self.get_total_price()
        return Decimal('0')

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()
