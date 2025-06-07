# repayments/models.py
from django.db import models
from django.utils import timezone
from loans.models import Loan

class RepaymentSchedule(models.Model):
    STATUS_CHOICES = [
        ('due', 'Due'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='repayment_schedules'
    )
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='due'
    )

    def __str__(self):
        return f"Repayment Schedule for Loan #{self.loan.id} due on {self.due_date}"

    class Meta:
        ordering = ['due_date']

class Repayment(models.Model):
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='repayments'
    )
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(
        max_length=50,
        choices=[
            ('cash', 'Cash'),
            ('bank_transfer', 'Bank Transfer'),
            ('mobile_money', 'Mobile Money'),
        ],
        default='cash'
    )

    def __str__(self):
        return f"Repayment of {self.amount} for Loan #{self.loan.id} on {self.date}"

    class Meta:
        ordering = ['date']