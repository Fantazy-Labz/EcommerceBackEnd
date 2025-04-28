from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User, Address
from apps.products.models import Product
from .utils import OrderManager

# Create your models here.

class Order(models.Model):
    
    ORDER_STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
    )

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    notes=models.TextField(blank=True)
    order_number=models.CharField(OrderManager.generate_order_number,max_length=255, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.email} - {self.status}"
    

class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(OrderManager.get_order_total_price,max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OrderItem {self.id} - {self.order.id} - {self.product.name}"


class Cart(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    session_id = models.CharField(OrderManager.get_session_id,max_length=255, blank=True, null=True)
    total_price = models.DecimalField(OrderManager.get_cart_total_price,max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cart_items_count = models.PositiveIntegerField(OrderManager.get_cart_items_count, default=0)

    def __str__(self):
        return f"Cart {self.id} - {self.user.email}"
    

class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='cart_items')
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CartItem {self.id} - {self.cart.id} - {self.product.name}"