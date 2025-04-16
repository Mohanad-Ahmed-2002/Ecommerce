from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,CartItem,CustomerOrder,OrderForm,Government,OrderItem,PromoCode
from django.contrib import messages
from decimal import Decimal
from django.http import JsonResponse
from .services import order_service,cart_service,product_service

# Create your views here.

def home(request):
    return render(request,'store/home.html')

def products_home(request):
    price_filter = request.GET.get('price')
    category_filter = request.GET.get('category')
    products = product_service.filter_products(price_filter, category_filter)

    context = {'products': products}
    return render(request, 'store/products.html', context)

def product_detail(request,product_id):

    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

def cart_detail(request):
    session_key = cart_service.get_or_create_session_key(request)
    cart_items, total_price = cart_service.get_cart_items_and_total(session_key)

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }

    return render(request, 'store/cart_detail.html', context)

def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = cart_service.add_product_to_cart(product_id, request)
        messages.success(request, f'"{product.name}" has been added to your cart successfully!')
    return redirect('products')

def increase_quantity(request, item_id):
    cart_service.increase_cart_item_quantity(item_id, request)
    return redirect('cart_detail')

def decrease_quantity(request, item_id):
    cart_service.decrease_cart_item_quantity(item_id,request)
    return redirect('cart_detail')

def checkout(request):

    form = OrderForm(request.POST or None)
    
    session_key = request.session.session_key   
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    price_data = order_service.calculate_total_prices(session_key)
    subtotal = Decimal(price_data['subtotal'])

    shipping_fee = Decimal(0)
    government_id = request.POST.get('government')

    if request.method == 'POST' and government_id:
        shipping_fee = order_service.get_shipping_fee(government_id)

    promo_code_str = request.POST.get('promo_code', '').strip()
    discount_amount = order_service.apply_promo_code(promo_code_str, subtotal, request)

    grand_total = subtotal - discount_amount + shipping_fee


    if request.method == 'POST':
        if form.is_valid():
            order = form.save(commit=False)
            order.shipping_fee = shipping_fee
            order.total_price = grand_total
            order_service.create_order(order, session_key)
            messages.success(request, "Your order has been placed successfully!")
            return redirect('order_success', order_id=order.id)

    governments = Government.objects.all()

    return render(request, 'store/checkout.html', {
        'form': form,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'grand_total': grand_total,
        'governments': governments,
        'discount_amount': discount_amount if discount_amount > 0 else None
    })

def order_success(request,order_id):
    order = get_object_or_404(CustomerOrder, id=order_id)
    order_items = order.order_items.all()

    order_id=order.id
    context = {
        'order': order,
        'order_items': order_items
    }

    return render(request,'store/order_success.html',context)

def privacy_policy(request):    

    return render(request, 'store/privacy_policy.html')

def validate_promo_code(request):
    code = request.GET.get('code', '').strip()
    subtotal = Decimal(request.GET.get('subtotal', '0'))
    
    discount = order_service.apply_promo_code(code, subtotal)  # request مش محتاجينها هنا

    if discount > 0:
        return JsonResponse({'valid': True, 'discount': float(discount)})
    else:
        return JsonResponse({'valid': False, 'message': 'Promo code is not valid or expired'})
