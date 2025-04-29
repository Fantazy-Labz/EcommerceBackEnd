from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.
    """
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'adress', 'status',
            'total_amount', 'stripe_payment_intent', 'notes', 
            'created_at', 'updated_at', "order_number"
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the OrderItem model.
    """
    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'product', 'quantity',
            'unit_price', 'total_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for the Cart model.
    """
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'session_id', 'total_price',
            'created_at', 'updated_at', 'cart_items_count'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at',"cart_items_count","total_price","session_id")


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the CartItem model.
    """
    class Meta:
        model = CartItem
        fields = [
            'id', 'cart', 'product', 'quantity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
       