from decimal import Decimal
from store.models import CartItem
from .models import  Government
from datetime import date


class CartService:

    def __init__(self,session_key):
        self.session_key = session_key
    
    def calculate_total_price(self):
        subtotal=Decimal(0)
        cart_items=CartItem.objects.filter(session_key=self.session_key)
        for item in cart_items :
            subtotal+=Decimal(item.get_total_price())
        
        shipping_fee=Decimal(70)
        total=subtotal+shipping_fee

        return {
            'subtotal':subtotal,
            'shipping_fee':shipping_fee,
            'total':total
        }

    def clear_cart(self):
        CartItem.objects.filter(session_key=self.session_key).delete()

class PricingService:

    def __init__(self,session_key,government_id=None):
        self.session_key=session_key
        self.government_id=government_id
        self.cart_service=CartService(session_key)

    def calculate_prices(self):
        price_data=self.cart_service.calculate_total_price()
        subtotal=Decimal(price_data['subtotal'])
        shipping_fee=self.calculate_shipping_fee(subtotal)
        grand_total=subtotal+shipping_fee

        return subtotal,shipping_fee,grand_total

    def calculate_shipping_fee(self,subtotal):

        shipping_fee=Decimal(0)
        
        if self.government_id:
            try:
                selected_government=Government.objects.get(id=self.government_id)
                shipping_fee=Decimal(selected_government.shipping_fee)
            except Government.DoesNotExist:
                shipping_fee=Decimal(70)
        return shipping_fee
