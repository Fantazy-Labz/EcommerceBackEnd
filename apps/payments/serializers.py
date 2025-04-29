from rest_framework import serializers
from .models import Payment, Refund

class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Payment model.
    """
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'payment_method',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')

class RefundSerializer(serializers.ModelSerializer):
    """
    Serializer for the Refund model.
    """
    class Meta:
        model = Refund
        fields = [
            'id', 'payment', 'amount', 'reason',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')

class CheckoutSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(required=True)
    contact_phone = serializers.CharField(required=True)
    payment_method = serializers.CharField(default='card')