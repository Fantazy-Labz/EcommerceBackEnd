from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem
from apps.products.models import Product

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'unit_price', 'total_price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Edición
            return self.readonly_fields + ('user', 'payment')
        return self.readonly_fields
    
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)

