from django.contrib import admin
from .models import Product, CustomerOrder, Government, OrderItem,PromoCode
from django.core.exceptions import ObjectDoesNotExist

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category','product_code']
    list_filter = ['category']

@admin.register(CustomerOrder)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'address', 'phone', 'total_price', 'order_date','government', 'get_product_codes']
    search_fields = ['name', 'phone']
    list_filter = ['order_date']

    def get_product_codes(self, obj):
        product_codes = []
        for item in obj.order_items.all():
            try:
                product = item.get_product()  # الحصول على المنتج باستخدام الدالة get_product
                product_codes.append(f"{product.product_code} * ({item.quantity})")
            except Product.DoesNotExist:
                product_codes.append("Product Not Found")  # أو أي رسالة تريد إظهارها في حالة عدم وجود المنتج
        return ", ".join(product_codes)

    get_product_codes.short_description = 'Product Codes'  # اسم العمود في الـ admin


@admin.register(Government)
class GovernmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'shipping_fee')


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percentage', 'is_active', 'expiration_date']
    search_fields = ['code']