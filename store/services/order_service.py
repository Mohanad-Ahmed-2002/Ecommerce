from decimal import Decimal
from store.models import CartItem, OrderItem, Government, PromoCode
from django.contrib import messages

def calculate_total_prices(session_key):
    
    subtotal=Decimal(0)
    cart_items=CartItem.objects.filter(session_key=session_key)

    for item in cart_items:
        subtotal+=Decimal(item.get_total_price())
    
    shipping_fee=Decimal(70)
    total=subtotal+shipping_fee
    
    return{
        'subtotal':subtotal,
        'shipping_fee':shipping_fee,
        'total':total
    }

def get_shipping_fee(government_id):

    try:
        selected_government=Government.objects.get(id=government_id)
        return Decimal(selected_government.shipping_fee)
    except Government.DoesNotExist:
        return Decimal(70)

def apply_promo_code(promo_code_str,subtotal,request=None):

    discount_amount=Decimal(0)

    if promo_code_str:
        try:
            promo=PromoCode.objects.get(code__iexact=promo_code_str)
            if promo.is_valid():
                discount_amount=(subtotal*promo.discount_percentage)/100
                if request:
                    messages.success(request,f"Promo code applied! You saved LE {discount_amount:.2f}")
            else:
                if request:
                    messages.error(request, "Promo code is not valid or expired.")
        except PromoCode.DoesNotExist:
            if request:
                messages.error(request, "Promo code not found.")
    return discount_amount

def create_order(order, session_key):

    order.save()
    cart_items = CartItem.objects.filter(session_key=session_key)
    
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product_code=item.product.product_code,
            quantity=item.quantity
        )
        
    cart_items.delete()