from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,CartItem,CustomerOrder,OrderForm,Government
from django.contrib import messages
from decimal import Decimal


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
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'store/cart_detail.html', context)

def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)

        # التحقق إذا كان المنتج موجود بالفعل في السلة
        cart_item, created = CartItem.objects.get_or_create(product=product, user=request.user)
    
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        messages.success(request, f'"{product.name}" has been added to your cart successfully!')

    return redirect('products')  

def increase_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart_detail')

def decrease_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()  # يتم حذف العنصر إذا كانت الكمية 1 وتم الضغط على زر النقصان
    return redirect('cart_detail')

def checkout(request):

    form=OrderForm(request.POST or None)
    price_data  = calculate_total_price(request)
    subtotal = Decimal(price_data['subtotal'])
    shipping_fee =  Decimal(0)
    government_id = request.POST.get('government')

    if request.method == 'POST' and 'government' in request.POST:
        government_id = request.POST.get('government')
        if government_id:
            try:
                selected_government = Government.objects.get(id=government_id)
                shipping_fee = Decimal(selected_government.shipping_fee)
            except Government.DoesNotExist:
                shipping_fee = Decimal(70)  # شحن افتراضي
    
    grand_total = subtotal + shipping_fee

    if request.method =='POST':


        if form.is_valid(): 
            order=form.save(commit=False)
            order.user=request.user
            order.shipping_fee = shipping_fee
            order.total_price = subtotal + shipping_fee
            order.save()
            messages.success(request, "Your order has been placed successfully!")
            request.session['cart'] = {} 
            return redirect ('order_success',order_id=order.id)
    else:
        form=OrderForm()

    governments = Government.objects.all()  # جلب جميع المحافظات


    return render(request, 'store/checkout.html', {
        'form':form,'subtotal':subtotal,'shipping_fee':shipping_fee,'grand_total':grand_total,'governments': governments
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

def calculate_total_price(request):

    subtotal = Decimal(0)
    cart_items = CartItem.objects.all()  # <-- استخدام CartItem بدلاً من session
    for item in cart_items:
        subtotal += Decimal(item.get_total_price())
    
    shipping_fee = Decimal(70)
    total = subtotal+shipping_fee 
    return {
        'subtotal':subtotal,
        'shipping_fee':shipping_fee,
        'total':total
    }

def privacy_policy(request):
    return render(request, 'store/privacy_policy.html')