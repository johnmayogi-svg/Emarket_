
from django import template
from shop.models import Product

register = template.Library()

@register.filter
def product_from_id(value):
    try:
        return Product.objects.get(id=value)
    except Product.DoesNotExist:
        return None

@register.filter
def mul(value, arg):
    return float(value) * float(arg)

@register.filter
def get_cart_total(cart):
    total = 0
    for pid, qty in cart.items():
        try:
            product = Product.objects.get(id=pid)
            total += product.price * qty
        except Product.DoesNotExist:
            continue
    return "%.2f" % total
