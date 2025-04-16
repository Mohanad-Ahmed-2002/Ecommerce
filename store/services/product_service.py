from store.models import Product

def filter_products(price_filter=None, category_filter=None):
    products = Product.objects.all()

    # فلترة السعر
    if price_filter == 'low':
        products = products.filter(price__lt=500)
    elif price_filter == 'mid':
        products = products.filter(price__gte=500, price__lte=1000)
    elif price_filter == 'high':
        products = products.filter(price__gt=1000)

    # فلترة الفئة
    category_mapping = {
        'Sunglasses': 'Sunglasses',
        'Eyeglasses': 'Eyeglasses',
        'Contact Lenses': 'Contact Lenses'
    }
    if category_filter:
        category = category_mapping.get(category_filter, category_filter)
        products = products.filter(category__name=category)

    return products
