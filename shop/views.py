from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from .forms import AddToCartForm
from django.urls import reverse
from decimal import Decimal

def product_list(request):
    products = Product.objects.all().order_by("-created")
    return render(request, "shop/product_list.html", {"products": products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    form = AddToCartForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        qty = form.cleaned_data["quantity"]
        cart = request.session.get("cart", {})
        pid = str(product.id)
        cart[pid] = cart.get(pid, 0) + qty
        request.session["cart"] = cart
        return redirect("cart")
    return render(request, "shop/product_detail.html", {"product": product, "form": form})

def cart_view(request):
    cart = request.session.get("cart", {})
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)
    items = []
    total = Decimal("0.00")
    for p in products:
        qty = cart.get(str(p.id), 0)
        subtotal = p.price * qty
        items.append({"product": p, "quantity": qty, "subtotal": subtotal})
        total += subtotal
    if request.method == "POST":
        # Simple "checkout" stub: clear cart and show thank you
        request.session["cart"] = {}
        return render(request, "shop/cart.html", {"items": items, "total": total, "paid": True})
    return render(request, "shop/cart.html", {"items": items, "total": total, "paid": False})
