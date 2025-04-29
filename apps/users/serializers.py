from rest_framework import serializers
from .models import User, Address

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'last_name', 
            'is_active', "phone_number", "is_email_verified",
            'created_at', 'updated_at', "verification_token"
        ]
        read_only_fields = ('id', 'created_at', 'updated_at', "is_email_verified" , "is_active", "verification_token")


class AdressSerializer(serializers.ModelSerializer):
    """
    Serializer for the Adress model.
    """
    class Meta:
        model = Address
        fields = [
            'id', 'user', 'adress_line1', 'adress_line2', 
            'city', 'state', 'postal_code', 'country',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')


