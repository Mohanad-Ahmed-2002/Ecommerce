from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,CartItem,CustomerOrder,OrderForm,Government,OrderItem,PromoCode,PromoCodeForm
from django.contrib import messages
from decimal import Decimal
from .cart_services import CartService,PricingService
from django.utils import timezone

# Create your views here.

def home(request):
    return render(request,'store/home.html')

def products_home(request):
    
    products=Product.objects.all()

    # فلترة حسب السعر
    price_filter = request.GET.get('price')
    if price_filter == 'low':
        products = products.filter(price__lt=500)
    elif price_filter == 'mid':
        products = products.filter(price__gte=500, price__lte=1000)
    elif price_filter == 'high':
        products = products.filter(price__gt=1000)

    # فلترة حسب الفئة
    category_filter = request.GET.get('category')

    category_mapping = {
            'Sunglasses': 'Sunglasses',
            'Eyeglasses': 'Eyeglasses',
            'Contact Lenses': 'Contact Lenses'
        }
    if category_filter:
        category_filter = category_mapping.get(category_filter, category_filter)
        products = products.filter(category__name=category_filter)
    context = {'products': products}


    return render(request,'store/products.html',context)

def product_detail(request,product_id):

    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

def cart_detail(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart_items = CartItem.objects.filter(session_key=session_key)

    # حساب إجمالي السعر باستخدام Decimal لضمان دقة الحسابات
    total_price = sum(Decimal(item.get_total_price()) for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }

    return render(request, 'store/cart_detail.html', context)

def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)

        # التحقق إذا كان المنتج موجود بالفعل في السلة باستخدام session_key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        cart_item, created = CartItem.objects.get_or_create(product=product, session_key=session_key)

        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        messages.success(request, f'"{product.name}" has been added to your cart successfully!')

    return redirect('products')

def increase_quantity(request, item_id):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart_item = get_object_or_404(CartItem, id=item_id, session_key=session_key)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart_detail')

def decrease_quantity(request, item_id):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart_item = get_object_or_404(CartItem, id=item_id, session_key=session_key)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_detail')

def checkout(request):
    order_form = OrderForm(request.POST or None)
    promo_form = PromoCodeForm(request.POST or None)

    # تأكيد وجود session
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    # الحصول على المحافظة المختارة
    government_id = request.POST.get('government')
    pricing_service = PricingService(session_key, government_id)

    # حساب الفاتورة
    try:
        subtotal, shipping_fee, grand_total = pricing_service.calculate_prices()
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('checkout')

    # التحقق من كود الخصم
    discount_amount = Decimal('0.00')
    promo_code = None

    if request.method == 'POST' and promo_form.is_valid():
        code_input = promo_form.cleaned_data['code']
        try:
            promo = PromoCode.objects.get(code__iexact=code_input)
            if promo.is_valid() and grand_total >= promo.min_order_value:
                promo_code = promo
                if promo.discount_type == 'percentage':
                    percentage = Decimal(str(promo.discount_value)) / Decimal('100')
                    discount_amount = (grand_total * percentage).quantize(Decimal('0.01'))
                else:
                    discount_amount = Decimal(str(promo.discount_value))
                grand_total = (grand_total - discount_amount).quantize(Decimal('0.01'))
            else:
                promo_form.add_error('code', 'Promo code expired or order value too low.')
        except PromoCode.DoesNotExist:
            promo_form.add_error('code', 'Promo code not found.')

    # تأكيد الطلب
    if request.method == 'POST' and order_form.is_valid():
        order = order_form.save(commit=False)
        order.shipping_fee = shipping_fee
        order.total_price = grand_total
        order.save()

        # نقل عناصر السلة إلى الطلب
        cart_items = CartItem.objects.filter(session_key=session_key)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product_code=item.product.product_code,
                quantity=item.quantity
            )

        # تفريغ السلة
        cart_items.delete()

        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_success', order_id=order.id)

    governments = Government.objects.all()

    return render(request, 'store/checkout.html', {
        'form': order_form,
        'promo_form': promo_form,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'discount': discount_amount,
        'grand_total': grand_total,
        'governments': governments,
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

