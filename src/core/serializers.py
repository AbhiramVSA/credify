from rest_framework import serializers
from .models import Customer


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for customer registration"""
    
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'monthly_income', 'phone_number']
        
    def validate_age(self, value):
        """Validate age is reasonable"""
        if value < 18:
            raise serializers.ValidationError("Customer must be at least 18 years old.")
        if value > 120:
            raise serializers.ValidationError("Age must be less than 120.")
        return value
    
    def validate_monthly_income(self, value):
        """Validate monthly income is positive"""
        if value <= 0:
            raise serializers.ValidationError("Monthly income must be greater than 0.")
        return value
    
    def validate_phone_number(self, value):
        """Additional phone number validation"""
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        if len(value) < 7 or len(value) > 15:
            raise serializers.ValidationError("Phone number must be between 7 and 15 digits.")
        return value


class CustomerResponseSerializer(serializers.ModelSerializer):
    """Serializer for customer registration response"""
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'age', 'monthly_income', 'approved_limit', 'phone_number']
    
    def get_name(self, obj):
        """Return full name"""
        return f"{obj.first_name} {obj.last_name}".strip()