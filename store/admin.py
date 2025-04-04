from django.contrib import admin
from .models import Product,CustomerOrder,Government

# Register your models here.
@admin.register(Product)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category']
    list_filter = ['category']
    
@admin.register(CustomerOrder)
class OrderAdmin(admin.ModelAdmin):

    list_display = ['id', 'name' ,'address', 'phone', 'total_price', 'order_date']
    search_fields = ['user__username', 'phone']
    list_filter = ['order_date']

@admin.register(Government)
class GovernmentAdmin(admin.ModelAdmin):

    list_display = ('name','shipping_fee')