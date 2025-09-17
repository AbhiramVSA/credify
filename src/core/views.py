from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import IntegrityError
from .models import Customer
from .serializers import (
    CustomerRegistrationSerializer, 
    CustomerResponseSerializer,
    LoanEligibilityRequestSerializer,
    LoanEligibilityResponseSerializer,
    LoanCreationRequestSerializer,
    LoanCreationResponseSerializer,
    LoanViewResponseSerializer,
    LoanListItemSerializer
)
from services.customer_service import LoanEligibilityService, LoanCreationService
from .models import Loan
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
            "register": "/register (POST) - Register a new customer",
            "check-eligibility": "/check-eligibility (POST) - Check loan eligibility",
            "create-loan": "/create-loan (POST) - Process a new loan",
            "view-loan": "/view-loan/{loan_id} (GET) - View loan details"
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


@api_view(['POST'])
def check_loan_eligibility(request):
    """
    Check loan eligibility based on customer credit score and other factors.
    
    Credit score is calculated based on:
    - Past loans paid on time
    - Number of loans taken in the past
    - Loan activity in current year
    - Loan approved volume
    - If sum of current loans > approved limit, credit score = 0
    
    Approval criteria:
    - credit_score > 50: approve loan
    - 50 > credit_score > 30: approve with interest rate > 12%
    - 30 > credit_score > 10: approve with interest rate > 16%
    - credit_score <= 10: don't approve
    - If sum of all current EMIs > 50% of monthly salary: don't approve
    """
    try:
        # Validate input data
        serializer = LoanEligibilityRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "error": "Validation failed",
                    "details": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract validated data
        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']
        
        # Check eligibility using the service
        eligibility_result = LoanEligibilityService.check_eligibility(
            customer_id=customer_id,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            tenure=tenure
        )
        
        # Handle service errors
        if 'error' in eligibility_result:
            return Response(
                {
                    "error": eligibility_result['error']
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Serialize and return response
        response_serializer = LoanEligibilityResponseSerializer(data=eligibility_result)
        if response_serializer.is_valid():
            logger.info(f"Loan eligibility checked for customer {customer_id}: {eligibility_result['approval']}")
            return Response(
                response_serializer.validated_data,
                status=status.HTTP_200_OK
            )
        else:
            logger.error(f"Response serialization failed: {response_serializer.errors}")
            return Response(
                eligibility_result,  # Return raw data if serialization fails
                status=status.HTTP_200_OK
            )
        
    except Exception as e:
        logger.error(f"Unexpected error during loan eligibility check: {str(e)}")
        return Response(
            {
                "error": "Internal server error",
                "details": "An unexpected error occurred during eligibility check"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def create_loan(request):
    """
    Process a new loan based on eligibility.
    
    This endpoint:
    1. Checks loan eligibility using the same logic as /check-eligibility
    2. If approved, creates a new loan record
    3. Returns loan details or rejection message
    """
    try:
        # Validate input data
        serializer = LoanCreationRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "error": "Validation failed",
                    "details": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract validated data
        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']
        
        # Create loan using the service
        loan_result = LoanCreationService.create_loan(
            customer_id=customer_id,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            tenure=tenure
        )
        
        # Serialize and return response
        response_serializer = LoanCreationResponseSerializer(data=loan_result)
        if response_serializer.is_valid():
            response_status = status.HTTP_201_CREATED if loan_result['loan_approved'] else status.HTTP_200_OK
            logger.info(f"Loan creation processed for customer {customer_id}: {loan_result['loan_approved']}")
            return Response(
                response_serializer.validated_data,
                status=response_status
            )
        else:
            logger.error(f"Response serialization failed: {response_serializer.errors}")
            return Response(
                loan_result,  # Return raw data if serialization fails
                status=status.HTTP_200_OK
            )
        
    except Exception as e:
        logger.error(f"Unexpected error during loan creation: {str(e)}")
        return Response(
            {
                "error": "Internal server error",
                "details": "An unexpected error occurred during loan creation"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def view_loan(request, loan_id):
    """
    View loan details and customer details for a specific loan.
    
    Returns comprehensive information about the loan and associated customer.
    """
    try:
        # Get the loan with customer details
        try:
            loan = Loan.objects.select_related('customer').get(loan_id=loan_id)
        except Loan.DoesNotExist:
            return Response(
                {
                    "error": "Loan not found",
                    "details": f"No loan found with ID {loan_id}"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Serialize and return loan details
        serializer = LoanViewResponseSerializer(loan)
        
        logger.info(f"Loan details retrieved for loan_id {loan_id}")
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Unexpected error retrieving loan {loan_id}: {str(e)}")
        return Response(
            {
                "error": "Internal server error",
                "details": "An unexpected error occurred while retrieving loan details"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    """
    View all current loan details by customer ID
    
    Args:
        request: The HTTP request
        customer_id: UUID of the customer
        
    Returns:
        Response with list of loan details or error message
    """
    try:
        logger.info(f"Retrieving all loans for customer_id {customer_id}")
        
        # Check if customer exists
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            logger.warning(f"Customer with ID {customer_id} not found")
            return Response(
                {
                    "error": "Customer not found",
                    "details": f"No customer found with ID {customer_id}"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all loans for the customer
        loans = Loan.objects.filter(customer=customer).order_by('-date_of_approval')
        
        if not loans.exists():
            logger.info(f"No loans found for customer_id {customer_id}")
            return Response([], status=status.HTTP_200_OK)
        
        # Serialize the loans data
        serializer = LoanListItemSerializer(loans, many=True)
        
        logger.info(f"Retrieved {loans.count()} loans for customer_id {customer_id}")
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Unexpected error retrieving loans for customer {customer_id}: {str(e)}")
        return Response(
            {
                "error": "Internal server error",
                "details": "An unexpected error occurred while retrieving customer loans"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
