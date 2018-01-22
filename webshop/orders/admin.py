from django.contrib import admin

from .models import Order, OrderItem


# 把OrderItem引用为Order的内联(相当于子)模型，使得可以在同一页上编辑两个模型
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    # 不按下拉列表的方式显示
    raw_id_fields = ['product']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email',
                    'address', 'postal_code', 'city', 'paid',
                    'created', 'updated']
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]


admin.site.register(Order, OrderAdmin)
