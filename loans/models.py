from django.db import models
from decimal import Decimal
from django.utils import timezone
from django.conf import settings
from dateutil.relativedelta import relativedelta

class LoanProduct(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Loan(models.Model):
    CURRENCY_CHOICES = [
        ('GHS', 'Ghana Cedi'),
        ('USD', 'US Dollar'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    borrower        = models.ForeignKey('borrowers.Borrower', on_delete=models.CASCADE)
    product         = models.ForeignKey(LoanProduct, on_delete=models.CASCADE)
    currency        = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GHS')
    principal       = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate   = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    start_date      = models.DateField()
    term_months     = models.PositiveIntegerField(default=3)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_rollover     = models.BooleanField(default=False)
    rollover_count  = models.PositiveIntegerField(default=0)
    original_term_months = models.PositiveIntegerField(default=3)
    description     = models.TextField(blank=True, null=True)
    created_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    def save(self, *args, **kwargs):
        # Set default interest_rate if none provided
        if self.interest_rate is None:
            if self.currency == 'GHS':
                self.interest_rate = Decimal('10.00')
            elif self.currency == 'USD':
                self.interest_rate = Decimal('9.00')
            else:
                self.interest_rate = Decimal('10.00')
        # Set original_term_months on first save
        if not self.pk and not self.original_term_months:
            self.original_term_months = self.term_months
        # Update status based on repayments and due date
        self.update_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan #{self.id} to {self.borrower}"

    def get_due_date(self):
        """Calculate the due date based on the start date and total term (including rollovers)."""
        total_term = self.original_term_months + (self.rollover_count * self.original_term_months)
        return self.start_date + relativedelta(months=total_term)

    def get_monthly_interest_payment(self):
        """Calculate the monthly interest payment using the interest rate as a monthly rate."""
        return (self.principal * self.interest_rate) / Decimal('100')

    def get_total_interest(self):
        """Calculate the total interest over the loan term, including rollovers."""
        total_term = self.original_term_months + (self.rollover_count * self.original_term_months)
        return self.get_monthly_interest_payment() * Decimal(total_term)

    def get_total_to_pay(self):
        """Calculate the total expected amount (principal + total interest), including rollovers."""
        return self.principal + self.get_total_interest()

    def get_remaining_term_months(self):
        """Calculate the remaining months in the term based on the current date."""
        from datetime import datetime
        current_date = datetime.now().date()
        due_date = self.get_due_date()
        if current_date >= due_date:
            return 0
        months_remaining = (due_date.year - current_date.year) * 12 + due_date.month - current_date.month
        return max(0, months_remaining)

    def get_remaining_interest(self):
        """Calculate the remaining interest based on the remaining term."""
        if self.status == 'paid':
            return Decimal('0.00')
        remaining_months = self.get_remaining_term_months()
        return self.get_monthly_interest_payment() * Decimal(remaining_months)

    def get_total_paid(self):
        """Calculate the total amount paid via repayments."""
        total = sum(repayment.amount for repayment in self.repayments.all())
        print(f"Total paid for Loan #{self.id}: {total}")  # Debugging
        return total

    def get_remaining_amount_to_pay(self):
        """Calculate the remaining amount to pay, accounting for repayments."""
        if self.status == 'paid':
            return Decimal('0.00')
        total_to_pay = self.get_total_to_pay()
        total_paid = self.get_total_paid()
        remaining = max(Decimal('0.00'), total_to_pay - total_paid)
        print(f"Remaining amount for Loan #{self.id}: Total to pay={total_to_pay}, Total paid={total_paid}, Remaining={remaining}")  # Debugging
        return remaining

    def update_status(self):
        """Update the loan status based on repayments and due date."""
        from datetime import datetime
        total_to_pay = self.get_total_to_pay()
        total_paid = self.get_total_paid()
        due_date = self.get_due_date()
        current_date = datetime.now().date()

        if total_paid >= total_to_pay:
            self.status = 'paid'
        elif current_date > due_date and total_paid < total_to_pay:
            self.status = 'overdue'
        else:
            self.status = 'active'
        print(f"Updated status for Loan #{self.id}: {self.status}")  # Debugging