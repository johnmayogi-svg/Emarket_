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

    # Handle checkout
    if request.method == "POST" and "checkout" in request.POST:
        request.session["cart"] = {}
        return render(request, "shop/cart.html", {"items": [], "total": 0, "paid": True})

    # Build items for display
    for p in products:
        qty = cart.get(str(p.id), 0)
        subtotal = p.price * qty
        items.append({"product": p, "quantity": qty, "subtotal": subtotal})
        total += subtotal

    return render(request, "shop/cart.html", {"items": items, "total": total, "paid": False})

def add_to_cart(request, product_id):
    """
    Adds a product to the session-based cart.
    """
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get("quantity", 1))
        
        # Get existing cart from session
        cart = request.session.get("cart", {})
        
        # Update quantity if product is already in cart
        if str(product_id) in cart:
            cart[str(product_id)] += quantity
        else:
            cart[str(product_id)] = quantity
        
        # Save back to session
        request.session["cart"] = cart

    # Redirect to cart page after adding
    return redirect("cart")

def cart_view(request):
    cart = request.session.get("cart", {})
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)
    items = []
    total = Decimal("0.00")

    # Handle quantity updates
    if request.method == "POST" and "update_cart" in request.POST:
        for p in products:
            qty_key = f"quantity_{p.id}"
            new_qty = int(request.POST.get(qty_key, cart.get(str(p.id), 1)))
            if new_qty > 0:
                cart[str(p.id)] = new_qty
            else:
                cart.pop(str(p.id), None)
        request.session["cart"] = cart
        return redirect("cart")  # reload with updated quantities

    # Handle checkout
    if request.method == "POST" and "checkout" in request.POST:
        request.session["cart"] = {}
        return render(request, "shop/cart.html", {"items": [], "total": 0, "paid": True})

    # Build items for display
    for p in products:
        qty = cart.get(str(p.id), 0)
        subtotal = p.price * qty
        items.append({"product": p, "quantity": qty, "subtotal": subtotal})
        total += subtotal

    return render(request, "shop/cart.html", {"items": items, "total": total, "paid": False})

