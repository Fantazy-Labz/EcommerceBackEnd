# apps/products/serializers.py
from rest_framework import serializers
from .models import Category, Product, Review

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'slug', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')

class ProductSerializer(serializers.ModelSerializer):
    is_in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock',
            'category', 'is_active', 'slug', 'created_at',
            'updated_at', 'image', 'is_in_stock'
        ]
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at', 'is_in_stock')

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value

class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'product', 'product_name', 'user', 'user_email', 
            'rating', 'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'user_email', 'product_name', 'created_at', 'updated_at')

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("La calificación debe ser entre 1 y 5.")
        return value
