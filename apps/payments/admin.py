from django.contrib import admin
from .models import Payment, Refund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('user__email', 'user__username', 'stripe_payment_intent_id')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Edición
            return self.readonly_fields + ('user', 'cart', 'stripe_payment_intent_id', 'amount', 'currency')
        return self.readonly_fields


admin.site.register(Refund)