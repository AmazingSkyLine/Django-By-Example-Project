from django import forms

# 购物车商品数量的选择，可为字符串或整型，范围为1-20
PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartAddProductForm(forms.Form):
    # coerce 将数据转成int
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int)
    # 非必需 初始为False 隐藏输入
    update = forms.BooleanField(required=False,
                                initial=False,
                                widget=forms.HiddenInput)
