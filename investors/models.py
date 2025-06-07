# investors/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator
import math
from decimal import Decimal

class Investor(models.Model):
    # Personal Details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = PhoneNumberField()
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    region = models.CharField(
        max_length=2,
        choices=[
            ('CR', 'Central Region'),
            ('ER', 'Eastern Region'),
            ('GR', 'Greater Accra Region'),
            ('NR', 'Northern Region'),
            ('WR', 'Western Region'),
        ],
        blank=True,
        null=True,
    )
    id_document = models.FileField(
        upload_to='investor_docs/',
        blank=True,
        null=True,
        help_text="Upload the investor's identification document (e.g., passport, ID card)."
    )

    # Investment Details
    currency = models.CharField(
        max_length=3,
        choices=[
            ('GHS', 'Cedis (GHS)'),
            ('USD', 'Dollars (USD)'),
        ],
        default='GHS',
    )
    investment_period = models.IntegerField(
        validators=[MinValueValidator(3)],
        help_text="Investment period in months (minimum 3 months for one quarter).",
    )
    funds_available = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    profit_earned = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Total profit earned by the investor."
    )
    profit_paid = models.BooleanField(
        default=False,
        help_text="Indicates whether the profit has been paid to the investor."
    )
    profit_paid_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Date and time when the profit was paid."
    )
    last_profit_calculation = models.DateTimeField(
        null=True, blank=True,
        help_text="Date and time of the last profit calculation."
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        help_text="The admin/officer who created this record.",
    )
    created_at = models.DateTimeField(
        default=timezone.now,  # Default to current time for new records
        help_text="Date and time when the investor was added to the system."
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def total_invested(self):
        """Calculate the total amount invested (excluding withdrawals and earnings payments)."""
        deposits = self.transactions.filter(
            transaction_type__in=['deposit', 'topup']
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        withdrawals = self.transactions.filter(
            transaction_type__in=['withdrawal', 'return']
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        return deposits - withdrawals

    def calculate_quarterly_profit(self):
        """
        Calculate and apply the 4% quarterly profit based on the total invested amount.
        Returns the total profit added in this calculation.
        """
        total_invested = self.total_invested()
        if total_invested <= 0:
            return Decimal('0.00')

        # Determine the number of quarters since the last profit calculation
        now = timezone.now()
        if self.last_profit_calculation:
            time_diff = now - self.last_profit_calculation
        else:
            # If no previous calculation, use the creation date
            time_diff = now - self.created_at

        # Approximate quarters (1 quarter = 3 months = 90 days)
        days_per_quarter = 90
        quarters_passed = math.floor(time_diff.days / days_per_quarter)

        if quarters_passed < 1:
            return Decimal('0.00')

        # Calculate profit: 4% per quarter on total invested amount
        profit_per_quarter = total_invested * Decimal('0.04')
        total_profit = profit_per_quarter * quarters_passed

        if total_profit > 0:
            # Record the profit as a transaction
            InvestorTransaction.objects.create(
                investor=self,
                transaction_type='profit',
                amount=total_profit,
                created_by=self.created_by,
            )
            # Update investor's profit_earned and funds_available
            self.profit_earned += total_profit
            self.funds_available += total_profit
            self.last_profit_calculation = now
            # Reset profit_paid status when new profit is added
            self.profit_paid = False
            self.profit_paid_date = None
            self.save()

        return total_profit

    def get_full_name(self):
        """Return the investor's full name for admin display."""
        return f"{self.first_name} {self.last_name}"

class InvestorTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Initial Deposit'),
        ('topup', 'Top-Up'),
        ('withdrawal', 'Withdrawal'),
        ('return', 'Return Payment'),
        ('profit', 'Profit'),
    ]

    investor = models.ForeignKey(
        Investor,
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} for {self.investor}"