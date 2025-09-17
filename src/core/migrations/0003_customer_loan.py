# Generated manually for Customer and Loan models

from django.db import migrations, models
import django.core.validators
from decimal import Decimal
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_actor_released'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('customer_id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
                ('age', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(120)])),
                ('phone_number', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message='Phone number must be digits and can include an optional leading \'+\'. Length: 7-15 digits.', regex='^\\+?\\d{7,15}$')])),
                ('monthly_income', models.DecimalField(decimal_places=2, help_text='Monthly income in currency units.', max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('approved_limit', models.DecimalField(blank=True, decimal_places=2, help_text='Approved credit/loan limit for the customer.', max_digits=14, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Customer',
                'verbose_name_plural': 'Customers',
                'ordering': ['customer_id'],
            },
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('loan_id', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('loan_amount', models.DecimalField(decimal_places=2, max_digits=14, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('tenure', models.PositiveIntegerField(help_text='Total tenure (in months).', validators=[django.core.validators.MinValueValidator(0)])),
                ('interest_rate', models.DecimalField(decimal_places=2, help_text='Annual interest rate in percent (e.g. 8.20).', validators=[django.core.validators.MinValueValidator(Decimal('0.00')), django.core.validators.MaxValueValidator(Decimal('100.00'))], max_digits=5)),
                ('monthly_payment', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('emis_paid_on_time', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('date_of_approval', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loans', to='core.customer')),
            ],
            options={
                'verbose_name': 'Loan',
                'verbose_name_plural': 'Loans',
                'ordering': ['-date_of_approval'],
            },
        ),
    ]