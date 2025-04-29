from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User
from apps.orders.models import Order
# Create your models here.

class Payment(models.Model):
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('transfer', 'Bank Transfer'),
    )
    
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='payments')
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    currency = models.CharField(max_length=3, default='MXN')
    
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} - {self.user.email} - {self.status}"
    

class Refund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    reason = models.TextField(_('reason'), blank=True)
    status = models.CharField(_('status'), max_length=20, choices=Payment.PAYMENT_STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Refund {self.id} - {self.payment.id} - {self.status}"