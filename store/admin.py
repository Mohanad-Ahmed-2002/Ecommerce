from django.contrib import admin
from .models import Product, CustomerOrder, Government, OrderItem

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category','product_code']
    list_filter = ['category']

@admin.register(CustomerOrder)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'address', 'phone', 'total_price', 'order_date', 'get_product_codes']
    search_fields = ['name', 'phone']
    list_filter = ['order_date']

    def get_product_codes(self, obj):
        return ", ".join([
            f"{item.product_code} * ({item.quantity})" for item in obj.order_items.all()
        ])
    get_product_codes.short_description = 'Product Codes'  # اسم العمود في الـ admin

@admin.register(Government)
class GovernmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'shipping_fee')
