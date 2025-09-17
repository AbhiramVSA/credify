from decimal import Decimal
from django.db import models
from django.db.models import Sum, Count, Q, F, Max
from datetime import datetime, date
from typing import Dict, Tuple
import uuid
from core.models import Customer, Loan


class CreditScoringService:
    """Service for calculating customer credit scores based on loan history"""
    
    @staticmethod
    def calculate_credit_score(customer_id: uuid.UUID) -> int:
        """
        Calculate credit score out of 100 based on:
        i. Past Loans paid on time
        ii. No of loans taken in past
        iii. Loan activity in current year
        iv. Loan approved volume
        v. If sum of current loans > approved limit, credit score = 0
        """
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return 0
        
        # Check if sum of current loans > approved limit
        current_loans_sum = customer.loans.aggregate(
            total=Sum('loan_amount')
        )['total'] or Decimal('0')
        
        if current_loans_sum > customer.approved_limit:
            return 0
        
        # Get all customer loans
        loans = customer.loans.all()
        total_loans = loans.count()
        
        if total_loans == 0:
            return 50  # Neutral score for customers with no loan history
        
        # Component 1: Past Loans paid on time (30% weight)
        on_time_score = CreditScoringService._calculate_on_time_payment_score(loans)
        
        # Component 2: Number of loans taken in past (20% weight)
        loan_count_score = CreditScoringService._calculate_loan_count_score(total_loans)
        
        # Component 3: Loan activity in current year (25% weight)
        current_year_score = CreditScoringService._calculate_current_year_activity_score(loans)
        
        # Component 4: Loan approved volume (25% weight)
        volume_score = CreditScoringService._calculate_volume_score(
            current_loans_sum, customer.approved_limit
        )
        
        # Calculate weighted credit score
        credit_score = (
            on_time_score * 0.30 +
            loan_count_score * 0.20 +
            current_year_score * 0.25 +
            volume_score * 0.25
        )
        
        return min(100, max(0, int(credit_score)))
    
    @staticmethod
    def _calculate_on_time_payment_score(loans) -> float:
        """Calculate score based on on-time payments"""
        total_emis = loans.aggregate(total=Sum('tenure'))['total'] or 0
        on_time_emis = loans.aggregate(total=Sum('emis_paid_on_time'))['total'] or 0
        
        if total_emis == 0:
            return 50
        
        on_time_ratio = on_time_emis / total_emis
        return on_time_ratio * 100
    
    @staticmethod
    def _calculate_loan_count_score(total_loans: int) -> float:
        """Calculate score based on number of loans (more loans = better history)"""
        if total_loans == 0:
            return 0
        elif total_loans <= 2:
            return 30
        elif total_loans <= 5:
            return 60
        elif total_loans <= 10:
            return 80
        else:
            return 100
    
    @staticmethod
    def _calculate_current_year_activity_score(loans) -> float:
        """Calculate score based on current year loan activity"""
        current_year = datetime.now().year
        current_year_loans = loans.filter(
            date_of_approval__year=current_year
        ).count()
        
        if current_year_loans == 0:
            return 20  # Low score for no activity
        elif current_year_loans <= 2:
            return 70
        elif current_year_loans <= 4:
            return 90
        else:
            return 100
    
    @staticmethod
    def _calculate_volume_score(current_loans_sum: Decimal, approved_limit: Decimal) -> float:
        """Calculate score based on loan volume utilization"""
        if approved_limit == 0:
            return 0
        
        utilization_ratio = float(current_loans_sum / approved_limit)
        
        if utilization_ratio <= 0.3:
            return 100
        elif utilization_ratio <= 0.5:
            return 80
        elif utilization_ratio <= 0.7:
            return 60
        elif utilization_ratio <= 0.9:
            return 40
        else:
            return 20


class LoanEligibilityService:
    """Service for checking loan eligibility and calculating terms"""
    
    @staticmethod
    def check_eligibility(
        customer_id: uuid.UUID,
        loan_amount: float,
        interest_rate: float,
        tenure: int
    ) -> Dict:
        """
        Check loan eligibility based on credit score and other criteria
        """
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return {
                'customer_id': customer_id,
                'approval': False,
                'interest_rate': interest_rate,
                'corrected_interest_rate': interest_rate,
                'tenure': tenure,
                'monthly_installment': 0.0,
                'error': 'Customer not found'
            }
        
        # Calculate credit score
        credit_score = CreditScoringService.calculate_credit_score(customer_id)
        
        # Check EMI vs salary ratio
        monthly_installment = LoanEligibilityService._calculate_monthly_installment(
            loan_amount, interest_rate, tenure
        )
        
        current_emis = LoanEligibilityService._calculate_current_emis(customer)
        total_emis = current_emis + Decimal(str(monthly_installment))
        
        # Check if total EMIs > 50% of monthly salary
        emi_ratio = float(total_emis / customer.monthly_income)
        if emi_ratio > 0.5:
            return {
                'customer_id': customer_id,
                'approval': False,
                'interest_rate': interest_rate,
                'corrected_interest_rate': interest_rate,
                'tenure': tenure,
                'monthly_installment': float(monthly_installment),
                'reason': 'EMI exceeds 50% of monthly salary'
            }
        
        # Determine approval and corrected interest rate based on credit score
        approval, corrected_rate = LoanEligibilityService._determine_approval_and_rate(
            credit_score, interest_rate
        )
        
        return {
            'customer_id': customer_id,
            'approval': approval,
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_rate,
            'tenure': tenure,
            'monthly_installment': float(monthly_installment),
            'credit_score': credit_score  # For debugging
        }
    
    @staticmethod
    def _calculate_monthly_installment(loan_amount: float, interest_rate: float, tenure: int) -> Decimal:
        """Calculate monthly installment using compound interest formula"""
        principal = Decimal(str(loan_amount))
        rate = Decimal(str(interest_rate)) / 100 / 12  # Monthly rate
        n = tenure
        
        if rate == 0:
            return (principal / n).quantize(Decimal('0.01'))
        
        # EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
        compound_factor = (1 + rate) ** n
        emi = principal * rate * compound_factor / (compound_factor - 1)
        
        return emi.quantize(Decimal('0.01'))
    
    @staticmethod
    def _calculate_current_emis(customer: Customer) -> Decimal:
        """Calculate sum of current EMIs for active loans"""
        active_loans = customer.loans.filter(
            emis_paid_on_time__lt=F('tenure')  # Still has remaining EMIs
        )
        return active_loans.aggregate(
            total=Sum('monthly_payment')
        )['total'] or Decimal('0')
    
    @staticmethod
    def _determine_approval_and_rate(credit_score: int, requested_rate: float) -> Tuple[bool, float]:
        """
        Determine loan approval and corrected interest rate based on credit score
        """
        if credit_score > 50:
            # Approve loan with any interest rate
            return True, requested_rate
        elif 30 < credit_score <= 50:
            # Approve loans with interest rate > 12%
            if requested_rate > 12:
                return True, requested_rate
            else:
                return True, 12.0  # Correct to minimum rate
        elif 10 < credit_score <= 30:
            # Approve loans with interest rate > 16%
            if requested_rate > 16:
                return True, requested_rate
            else:
                return True, 16.0  # Correct to minimum rate
        else:
            # Don't approve any loans
            return False, requested_rate


class LoanCreationService:
    """Service for creating new loans"""
    
    @staticmethod
    def create_loan(
        customer_id: uuid.UUID,
        loan_amount: float,
        interest_rate: float,
        tenure: int
    ) -> Dict:
        """
        Create a new loan after checking eligibility
        """
        # First check eligibility
        eligibility_result = LoanEligibilityService.check_eligibility(
            customer_id=customer_id,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            tenure=tenure
        )
        
        # Handle customer not found
        if 'error' in eligibility_result:
            return {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': eligibility_result['error'],
                'monthly_installment': 0.0
            }
        
        # If not approved, return rejection message
        if not eligibility_result['approval']:
            reason = eligibility_result.get('reason', 'Loan not approved based on credit assessment')
            return {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': reason,
                'monthly_installment': eligibility_result['monthly_installment']
            }
        
        # If approved, create the loan
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            
            # Use corrected interest rate if provided
            final_interest_rate = eligibility_result['corrected_interest_rate']
            
            # Create the loan (UUID will be auto-generated)
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=Decimal(str(loan_amount)),
                tenure=tenure,
                interest_rate=Decimal(str(final_interest_rate)),
                monthly_payment=Decimal(str(eligibility_result['monthly_installment'])),
                date_of_approval=date.today(),
                emis_paid_on_time=0
            )
            
            return {
                'loan_id': loan.loan_id,
                'customer_id': customer_id,
                'loan_approved': True,
                'message': 'Loan approved successfully',
                'monthly_installment': eligibility_result['monthly_installment']
            }
            
        except Exception as e:
            return {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': f'Error creating loan: {str(e)}',
                'monthly_installment': eligibility_result['monthly_installment']
            }
