from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import IntegrityError
from .models import Customer
from .serializers import CustomerRegistrationSerializer, CustomerResponseSerializer
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def api_info(request):
    """
    API information endpoint for the root URL
    """
    return Response({
        "message": "Alemno Backend API",
        "version": "1.0.0",
        "endpoints": {
            "register": "/register (POST) - Register a new customer"
        }
    })


@api_view(['POST'])
def register_customer(request):
    """
    Register a new customer with automatic approved_limit calculation.
    
    Calculates approved_limit as 36 * monthly_income rounded to nearest lakh.
    """
    try:
        # Validate input data
        serializer = CustomerRegistrationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "error": "Validation failed",
                    "details": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create customer
        customer = serializer.save()
        
        # Return response with calculated approved_limit
        response_serializer = CustomerResponseSerializer(customer)
        
        logger.info(f"Customer {customer.customer_id} registered successfully")
        
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
        
    except IntegrityError as e:
        logger.error(f"Database integrity error during customer registration: {str(e)}")
        return Response(
            {
                "error": "Customer registration failed",
                "details": "A customer with this information may already exist"
            },
            status=status.HTTP_409_CONFLICT
        )
    
    except Exception as e:
        logger.error(f"Unexpected error during customer registration: {str(e)}")
        return Response(
            {
                "error": "Internal server error",
                "details": "An unexpected error occurred during registration"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
