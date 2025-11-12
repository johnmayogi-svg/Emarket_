from django.contrib import admin
from .models import Category, Product, Order, OrderItem

# ----------------------------
# Category Admin
# ----------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


# ----------------------------
# Product Admin
# ----------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'created')
    list_filter = ('category', 'created')
    search_fields = ('name', 'description')
    prepopulated_fields = {"slug": ("name",)}


# ----------------------------
# Inline for Order Items
# ----------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'get_total')

    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = "Subtotal"


# ----------------------------
# Order Admin
# ----------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_email', 'status', 'created_at', 'get_total')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'customer_email', 'customer_phone')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'get_total')

    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = "Total"


# ----------------------------
# OrderItem Admin (optional)
# ----------------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'get_total')
    readonly_fields = ('get_total',)

    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = "Subtotal"
