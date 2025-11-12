from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from decimal import Decimal
from django.http import JsonResponse
from .forms import AddToCartForm
from .models import Product, Order, OrderItem
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db import models

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('product_list')
    return redirect('login')

@login_required(login_url='login')
def product_list(request):
    products = Product.objects.all().order_by("-created")
    return render(request, "shop/product_list.html", {"products": products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    form = AddToCartForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        qty = form.cleaned_data["quantity"]
        cart = request.session.get("cart", {})
        cart[str(product.id)] = cart.get(str(product.id), 0) + qty
        request.session["cart"] = cart
        request.session.modified = True

        messages.success(request, f"{product.name} added to your cart!")
        return redirect("product_list")

    return render(request, "shop/product_detail.html", {"product": product, "form": form})


# -------------------------------
# Cart Views
# -------------------------------
def add_to_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        try:
            quantity = int(request.POST.get("quantity", 1))
            quantity = max(quantity, 1)
        except ValueError:
            quantity = 1

        cart = request.session.get("cart", {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
        request.session["cart"] = cart
        request.session.modified = True

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True, "cart_count": sum(cart.values())})

        messages.success(request, f"{product.name} added to your cart!")
        return redirect(request.META.get("HTTP_REFERER", "/"))

    return redirect("product_list")


def cart_view(request):
    cart = request.session.get("cart", {})
    items = []
    total = Decimal("0.00")

    if cart:
        products = Product.objects.filter(id__in=cart.keys())
        for product in products:
            qty = cart.get(str(product.id), 0)
            subtotal = product.price * qty
            total += subtotal
            items.append({
                "product": product,
                "quantity": qty,
                "subtotal": subtotal
            })

        # Handle quantity updates
        if request.method == "POST" and "update_cart" in request.POST:
            for product in products:
                key = f"quantity_{product.id}"
                try:
                    new_qty = int(request.POST.get(key, cart.get(str(product.id), 1)))
                    if new_qty > 0:
                        cart[str(product.id)] = new_qty
                    else:
                        cart.pop(str(product.id), None)
                except ValueError:
                    continue

            request.session["cart"] = cart
            request.session.modified = True

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "total": float(total)})

            messages.success(request, "Cart updated successfully!")
            return redirect("cart")

    return render(request, "shop/cart.html", {"items": items, "total": total})


# -------------------------------
# Checkout View
# -------------------------------
@login_required(login_url='login')
def checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        messages.info(request, "Your cart is empty.")
        return redirect("product_list")

    products = Product.objects.filter(id__in=cart.keys())
    items = []
    total = Decimal("0.00")

    if request.method == "POST" and "name" in request.POST and "email" in request.POST and "phone" in request.POST:
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")  # <-- new

        # Update session quantities if form allows editing
        for p in products:
            qty_str = request.POST.get(f"quantity_{p.id}")
            if qty_str:
                cart[str(p.id)] = int(qty_str)
        request.session["cart"] = cart

        # Create order linked to logged-in user
        order = Order.objects.create(
            user=request.user,
            customer_name=name,
            customer_email=email,
            customer_phone=phone,  # <-- save phone
        )

        # Create order items
        for p in products:
            qty = cart.get(str(p.id), 1)
            OrderItem.objects.create(
                order=order,
                product=p,
                quantity=qty,
                price=p.price,
            )

        # Clear cart after order
        request.session["cart"] = {}
        messages.success(request, "Your order has been placed successfully!")
        return render(request, "shop/order_success.html", {"order": order})

    # Build display data for the form
    for p in products:
        qty = cart.get(str(p.id), 0)
        subtotal = p.price * qty
        total += subtotal
        items.append({"product": p, "quantity": qty, "subtotal": subtotal})

    return render(request, "shop/checkout.html", {"items": items, "total": total})

# -------------------------------
# User Registration
# -------------------------------
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f"Account created for {username}!")
            return redirect("product_list")
    else:
        form = UserCreationForm()
    return render(request, "shop/register.html", {"form": form})


def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    products = Product.objects.all()
    orders = Order.objects.all()
    order_items = OrderItem.objects.all()

    # Basic stats
    total_products = products.count()
    total_orders = orders.count()
    total_sales = sum(order.get_total() for order in orders)

    # Orders by status
    orders_by_status = {
        status: orders.filter(status=status).count()
        for status, _ in Order.STATUS_CHOICES
    }

    # Top 5 best-selling products (by quantity sold)
    product_sales = (
        order_items
        .values('product__name')
        .annotate(total_quantity=models.Sum('quantity'))
        .order_by('-total_quantity')[:5]
    )

    context = {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_sales": total_sales,
        "orders_by_status": orders_by_status,
        "product_sales": product_sales,
        "recent_orders": orders.order_by('-created_at')[:10],  # latest 10 orders
    }

    return render(request, "shop/admin_dashboard.html", context)

@login_required(login_url='login')
def my_orders(request):
    """
    Display all orders for the currently logged-in user.
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "shop/my_orders.html", {"orders": orders})
