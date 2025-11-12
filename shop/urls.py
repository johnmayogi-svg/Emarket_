from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Default: show login first
    path('', views.home_redirect, name='home'),

    # Shop routes
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # Auth routes
    path('login/', auth_views.LoginView.as_view(template_name='shop/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
]

