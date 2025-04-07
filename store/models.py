from django.db import models
from django.contrib.auth.models import User
from django import forms


# Create your models here.

class Category(models.Model):
    CATEGORY_CHOICES = [
        ('Sunglasses', 'Sunglasses'),
        ('Eyeglasses', 'Eyeglasses'),
        ('ContactLenses', 'Contact Lenses'),
    ]
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  
    images = models.ImageField(upload_to='products/')
    product_code = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

class CartItem(models.Model):
    session_key = models.CharField(max_length=40, null=True, blank=True)  # بدل user    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

class Government(models.Model):
    name = models.CharField(max_length=100)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name}"

class CustomerOrder(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=11)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=6, decimal_places=2, default=70)
    order_date = models.DateTimeField(auto_now_add=True)
    government = models.ForeignKey(Government, on_delete=models.SET_NULL, null=True)

    def get_order_items(self):
        return self.order_items.all()  # جلب كل العناصر الخاصة بالطلب

    def save(self, *args, **kwargs):
        if self.government:
            self.shipping_fee = self.government.shipping_fee  # تحديد رسوم الشحن تلقائيًا
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.name}-{self.order_date}"

class OrderForm(forms.ModelForm):

    government = forms.ModelChoiceField(
        queryset=Government.objects.all(),
        empty_label="Select your governorate",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model=CustomerOrder
        fields=['name','email','address','phone','government']

class OrderItem(models.Model):
    order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    product_code = models.CharField(max_length=50)

    def get_product(self):
        return Product.objects.get(product_code=self.product_code)
    
    def __str__(self):
        return f"{self.get_product().name} - {self.quantity}"

