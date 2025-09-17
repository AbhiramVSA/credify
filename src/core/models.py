from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from decimal import Decimal


phone_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message="Phone number must be digits and can include an optional leading '+'. Length: 7-15 digits."
)


class Customer(models.Model):
    """
    Represents a customer (customer_data).
    Uses customer_id as the primary key because sample data includes explicit IDs.
    """
    customer_id = models.PositiveIntegerField(primary_key=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64, blank=True)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    phone_number = models.CharField(max_length=15, validators=[phone_validator], blank=True)
    monthly_salary = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Monthly salary in currency units."
    )
    approved_limit = models.DecimalField(
        max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Approved credit/loan limit for the customer."
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ["customer_id"]

    def __str__(self):
        return f"{self.customer_id} — {self.first_name} {self.last_name}".strip()


class Loan(models.Model):
    """
    Represents a loan (loan_data). Linked to Customer via ForeignKey.
    Assumes:
      - tenure: total number of EMIs (months) or unit consistent with your data
      - emis_paid_on_time: number of EMIs paid on time (integer)
      - date_of_approval and end_date are stored as DateField
    """
    loan_id = models.PositiveIntegerField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="loans")
    loan_amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    tenure = models.PositiveIntegerField(validators=[MinValueValidator(0)], help_text="Total tenure (in months).")
    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Annual interest rate in percent (e.g. 8.20)."
    )
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    emis_paid_on_time = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    date_of_approval = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Loan"
        verbose_name_plural = "Loans"
        ordering = ["-date_of_approval"]

    def __str__(self):
        # shows loan id and customer name for quick human read
        return f"Loan {self.loan_id} — {self.customer.first_name} {self.customer.last_name}".strip()

    @property
    def remaining_tenure(self):
        """
        Remaining number of EMIs (months). If emis_paid_on_time > tenure, returns 0.
        """
        remaining = self.tenure - self.emis_paid_on_time
        return remaining if remaining > 0 else 0

    @property
    def outstanding_balance_estimate(self):
        """
        Rough outstanding balance estimate = remaining_tenure * monthly_payment.
        Note: This is a simple estimate and not exact amortization.
        """
        return (Decimal(self.remaining_tenure) * self.monthly_payment).quantize(Decimal("0.01"))
