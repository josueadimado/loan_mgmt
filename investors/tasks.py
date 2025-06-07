# investors/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Investor, InvestorTransaction

@shared_task
def pay_investor_earnings():
    """Calculate and pay earnings for all investors based on their investment period."""
    today = timezone.now()
    for investor in Investor.objects.all():
        # Determine the last earnings payment date
        last_payment = investor.transactions.filter(
            transaction_type='return'
        ).order_by('-date').first()
        
        # Check if it's time to pay earnings based on the investment period
        if last_payment:
            last_payment_date = last_payment.date
            if investor.investment_period == 'monthly':
                next_payment_date = last_payment_date + timezone.timedelta(days=30)
            elif investor.investment_period == 'quarterly':
                next_payment_date = last_payment_date + timezone.timedelta(days=90)
            elif investor.investment_period == 'annually':
                next_payment_date = last_payment_date + timezone.timedelta(days=365)
            else:
                continue
            if today < next_payment_date:
                continue
        else:
            # If no previous payment, use created_at as the start date
            last_payment_date = investor.created_at
            if investor.investment_period == 'monthly':
                next_payment_date = last_payment_date + timezone.timedelta(days=30)
            elif investor.investment_period == 'quarterly':
                next_payment_date = last_payment_date + timezone.timedelta(days=90)
            elif investor.investment_period == 'annually':
                next_payment_date = last_payment_date + timezone.timedelta(days=365)
            else:
                continue
            if today < next_payment_date:
                continue

        # Calculate earnings for the period
        earning = investor.calculate_period_earning()
        if earning > 0:
            # Record the earnings payment as a transaction
            InvestorTransaction.objects.create(
                investor=investor,
                transaction_type='return',
                amount=earning,
                created_by=investor.created_by,  # Use the creator of the investor record
            )
            # Update funds_available (earnings are added to available funds)
            investor.funds_available += earning
            investor.save()