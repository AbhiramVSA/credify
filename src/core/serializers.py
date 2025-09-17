from rest_framework import serializers
from .models import Customer, Loan


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


class LoanEligibilityRequestSerializer(serializers.Serializer):
    """Serializer for loan eligibility check request"""
    customer_id = serializers.UUIDField()
    loan_amount = serializers.FloatField(min_value=0.01)
    interest_rate = serializers.FloatField(min_value=0.01, max_value=100.0)
    tenure = serializers.IntegerField(min_value=1, max_value=600)  # Max 50 years
    
    def validate_customer_id(self, value):
        """Validate that customer exists"""
        if not Customer.objects.filter(customer_id=value).exists():
            raise serializers.ValidationError("Customer does not exist.")
        return value


class LoanEligibilityResponseSerializer(serializers.Serializer):
    """Serializer for loan eligibility check response"""
    customer_id = serializers.UUIDField()
    approval = serializers.BooleanField()
    interest_rate = serializers.FloatField()
    corrected_interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()
    monthly_installment = serializers.FloatField()
    reason = serializers.CharField(required=False, allow_blank=True)
    credit_score = serializers.IntegerField(required=False)


class LoanCreationRequestSerializer(serializers.Serializer):
    """Serializer for loan creation request"""
    customer_id = serializers.UUIDField()
    loan_amount = serializers.FloatField(min_value=0.01)
    interest_rate = serializers.FloatField(min_value=0.01, max_value=100.0)
    tenure = serializers.IntegerField(min_value=1, max_value=600)  # Max 50 years
    
    def validate_customer_id(self, value):
        """Validate that customer exists"""
        if not Customer.objects.filter(customer_id=value).exists():
            raise serializers.ValidationError("Customer does not exist.")
        return value


class LoanCreationResponseSerializer(serializers.Serializer):
    """Serializer for loan creation response"""
    loan_id = serializers.UUIDField(allow_null=True)
    customer_id = serializers.UUIDField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField(required=False, allow_blank=True)
    monthly_installment = serializers.FloatField()


class CustomerDetailSerializer(serializers.ModelSerializer):
    """Serializer for customer details in loan view"""
    id = serializers.UUIDField(source='customer_id')
    
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'age']


class LoanViewResponseSerializer(serializers.ModelSerializer):
    """Serializer for loan view response"""
    customer = CustomerDetailSerializer(read_only=True)
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 'monthly_payment', 'tenure']
        
    def to_representation(self, instance):
        """Customize the response format"""
        data = super().to_representation(instance)
        # Rename monthly_payment to monthly_installment for consistency
        data['monthly_installment'] = data.pop('monthly_payment')
        return data


class LoanListItemSerializer(serializers.ModelSerializer):
    """Serializer for individual loan items in the loans list response"""
    monthly_installment = serializers.DecimalField(source='monthly_payment', max_digits=12, decimal_places=2)
    repayments_left = serializers.IntegerField(source='remaining_tenure')
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_installment', 'repayments_left']
        
    def to_representation(self, instance):
        """Customize the response format"""
        data = super().to_representation(instance)
        # Convert decimal fields to float for consistency with API spec
        data['loan_amount'] = float(data['loan_amount'])
        data['interest_rate'] = float(data['interest_rate'])
        data['monthly_installment'] = float(data['monthly_installment'])
        return data