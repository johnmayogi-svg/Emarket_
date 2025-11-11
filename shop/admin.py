from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, Order, OrderItem

# -------------------------------
# Order Admin
# -------------------------------
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'status_badge', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'customer_email')

    def status_badge(self, obj):
        color = {
            'Pending': 'orange',
            'Processing': 'blue',
            'Shipped': 'purple',
            'Delivered': 'green',
            'Cancelled': 'red',
        }.get(obj.status, 'gray')
        return format_html(
            '<span style="color:white; background-color:{}; padding:3px 8px; border-radius:5px;">{}</span>',
            color,
            obj.status
        )
    status_badge.short_description = 'Status'

admin.site.register(Order, OrderAdmin)

# -------------------------------
# OrderItem Admin
# -------------------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')

# -------------------------------
# Category Admin
# -------------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}

# -------------------------------
# Product Admin
# -------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "created")
    prepopulated_fields = {"slug": ("name",)}
