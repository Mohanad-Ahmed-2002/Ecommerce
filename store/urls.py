from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products_home, name='products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('checkout/',views.checkout,name='checkout'),
    path('order_success/<int:order_id>/', views.order_success, name='order_success'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('validate-promo/', views.validate_promo_code, name='validate_promo_code'),

]