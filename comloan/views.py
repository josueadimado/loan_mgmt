# loan_mgmt/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from loans.models import Loan
from borrowers.models import Borrower
from investors.models import Investor, InvestorTransaction
from repayments.models import Repayment
from exchange_rates.models import ExchangeRate
from exchange_rates.forms import ExchangeRateForm
from decimal import Decimal
from dateutil.relativedelta import relativedelta

@login_required
def dashboard(request):
    # Handle Exchange Rate Form
    exchange_rate = ExchangeRate.objects.filter(from_currency='USD', to_currency='GHS').first()
    if not exchange_rate:
        exchange_rate = ExchangeRate.objects.create(
            from_currency='USD',
            to_currency='GHS',
            rate=Decimal('15.0000'),
            last_updated=timezone.now()
        )
    rate_form = ExchangeRateForm(instance=exchange_rate)

    if request.method == 'POST':
        if 'update_rate' in request.POST:
            rate_form = ExchangeRateForm(request.POST, instance=exchange_rate)
            if rate_form.is_valid():
                rate_obj = rate_form.save(commit=False)
                rate_obj.last_updated = timezone.now()
                rate_obj.save()
                return redirect('dashboard')
        elif 'mark_profit_paid' in request.POST:
            investor_id = request.POST.get('investor_id')
            investor = Investor.objects.get(id=investor_id)
            investor.profit_paid = True
            investor.profit_paid_date = timezone.now()
            investor.save()
            return redirect('dashboard')

    # Check if exchange rate is outdated (e.g., older than 1 day)
    rate_outdated = (timezone.now() - exchange_rate.last_updated) > timedelta(days=1)

    # Get the USD-to-GHS exchange rate
    usd_to_ghs_rate = ExchangeRate.get_usd_to_ghs_rate()

    # Total Portfolio: Sum of all loans' total expected amount, converted to GHS
    loans = Loan.objects.all()
    total_portfolio = Decimal('0.00')
    for loan in loans:
        amount = loan.get_total_to_pay()
        if loan.currency == 'USD':
            amount = amount * usd_to_ghs_rate
        total_portfolio += amount

    # Active Loans: Count and value of loans with status 'active', converted to GHS
    active_loans = Loan.objects.filter(status='active')
    active_loans_count = active_loans.count()
    active_loans_value = Decimal('0.00')
    for loan in active_loans:
        amount = loan.get_total_to_pay()
        if loan.currency == 'USD':
            amount = amount * usd_to_ghs_rate
        active_loans_value += amount

    # Overdue Loans: Count and value of loans with status 'overdue', converted to GHS
    overdue_loans = Loan.objects.filter(status='overdue')
    overdue_loans_count = overdue_loans.count()
    overdue_loans_value = Decimal('0.00')
    for loan in overdue_loans:
        amount = loan.get_remaining_amount_to_pay()
        if loan.currency == 'USD':
            amount = amount * usd_to_ghs_rate
        overdue_loans_value += amount

    # Default Rate: Percentage of loans that are overdue
    total_loans_count = Loan.objects.count()
    default_rate = (overdue_loans_count / total_loans_count * 100) if total_loans_count > 0 else 0

    # Loans Due This Month: Calculate due date using start_date and term_months
    current_month_start = timezone.now().date().replace(day=1)
    next_month_start = (current_month_start + timedelta(days=32)).replace(day=1)
    loans_due_count = 0
    loans_due_value = Decimal('0.00')
    for loan in Loan.objects.filter(status='active'):
        # Calculate due date: start_date + term_months
        due_date = loan.start_date + relativedelta(months=loan.term_months)
        if current_month_start <= due_date < next_month_start:
            loans_due_count += 1
            amount = loan.get_remaining_amount_to_pay()
            if loan.currency == 'USD':
                amount = amount * usd_to_ghs_rate
            loans_due_value += amount

    # Loan Approval Rate (This Month): Percentage of loans created this month that are active
    current_month = timezone.now().month
    current_year = timezone.now().year
    loans_this_month = Loan.objects.filter(start_date__month=current_month, start_date__year=current_year)
    loans_this_month_count = loans_this_month.count()
    active_loans_this_month_count = loans_this_month.filter(status='active').count()
    loan_approval_rate = (active_loans_this_month_count / loans_this_month_count * 100) if loans_this_month_count > 0 else 0

    # Average Loan Amount: Average of all loans' total amount, converted to GHS
    average_loan_amount = Decimal('0.00')
    if loans.exists():
        total_amount = sum(
            loan.get_total_to_pay() * usd_to_ghs_rate if loan.currency == 'USD' else loan.get_total_to_pay()
            for loan in loans
        )
        average_loan_amount = total_amount / loans.count()

    # Total Interest Earned: Sum of interest from all loans, converted to GHS
    total_interest_earned = Decimal('0.00')
    for loan in loans:
        interest = loan.get_total_interest()
        if loan.currency == 'USD':
            interest = interest * usd_to_ghs_rate
        total_interest_earned += interest

    # Cash Flow (This Month): Sum of repayments made this month, converted to GHS
    repayments = Repayment.objects.filter(
        date__month=current_month,
        date__year=current_year
    ).select_related('loan')
    cash_flow = Decimal('0.00')
    for repayment in repayments:
        amount = repayment.amount
        if repayment.loan.currency == 'USD':
            amount = amount * usd_to_ghs_rate
        cash_flow += amount

    # Total Invested: Sum of total_invested() across all investors, converted to GHS
    investors = Investor.objects.all()
    total_invested = Decimal('0.00')
    for investor in investors:
        invested = investor.total_invested()
        if investor.currency == 'USD':
            invested = invested * usd_to_ghs_rate
        total_invested += invested

    # Potential Earnings: Calculate 4% quarterly earnings for all investors, converted to GHS
    potential_earnings = Decimal('0.00')
    for investor in investors:
        invested = investor.total_invested()
        if invested > 0:
            earnings = invested * Decimal('0.04')
            if investor.currency == 'USD':
                earnings = earnings * usd_to_ghs_rate
            potential_earnings += earnings

    # Total Borrowers and Investors
    total_borrowers = Borrower.objects.count()
    total_investors = Investor.objects.count()

    # Profit Distributed to Investors: Sum of profits where profit_paid=True, converted to GHS
    profit_distributed = Decimal('0.00')
    for investor in investors.filter(profit_paid=True):
        profit = investor.profit_earned
        if investor.currency == 'USD':
            profit = profit * usd_to_ghs_rate
        profit_distributed += profit

    # Investor Activity (This Month): Count of investor transactions this month
    investor_transactions = InvestorTransaction.objects.filter(
        date__month=current_month,
        date__year=current_year
    )
    investor_activity_count = investor_transactions.count()

    # Top Borrowers: Borrowers with the most loans and highest total due, converted to GHS
    top_borrowers = []
    for borrower in Borrower.objects.annotate(loan_count=Count('loan')).filter(loan_count__gt=0).order_by('-loan_count')[:5]:
        loans = Loan.objects.filter(borrower=borrower).prefetch_related('repayments')
        total_due = Decimal('0.00')
        for loan in loans:
            due = loan.get_remaining_amount_to_pay()
            if loan.currency == 'USD':
                due = due * usd_to_ghs_rate
            total_due += due
        top_borrowers.append({
            'first_name': borrower.first_name,
            'last_name': borrower.last_name,
            'loan_count': borrower.loan_count,
            'total_due': total_due
        })

    # Top Investors: Investors with the most funds available, converted to GHS
    top_investors = Investor.objects.order_by('-funds_available')[:5]
    for investor in top_investors:
        investor.funds_available_ghs = investor.funds_available
        investor.profit_earned_ghs = investor.profit_earned
        if investor.currency == 'USD':
            investor.funds_available_ghs = investor.funds_available * usd_to_ghs_rate
            investor.profit_earned_ghs = investor.profit_earned * usd_to_ghs_rate

    context = {
        'total_portfolio': total_portfolio,
        'active_loans_count': active_loans_count,
        'active_loans_value': active_loans_value,
        'overdue_loans_count': overdue_loans_count,
        'overdue_loans_value': overdue_loans_value,
        'default_rate': default_rate,
        'loans_due_count': loans_due_count,
        'loans_due_value': loans_due_value,
        'loan_approval_rate': loan_approval_rate,
        'average_loan_amount': average_loan_amount,
        'total_interest_earned': total_interest_earned,
        'cash_flow': cash_flow,
        'total_invested': total_invested,
        'potential_earnings': potential_earnings,
        'total_borrowers': total_borrowers,
        'total_investors': total_investors,
        'profit_distributed': profit_distributed,
        'investor_activity_count': investor_activity_count,
        'top_borrowers': top_borrowers,
        'top_investors': top_investors,
        'rate_form': rate_form,
        'rate_outdated': rate_outdated,
        'current_exchange_rate': exchange_rate.rate,
    }
    return render(request, 'dashboard.html', context)