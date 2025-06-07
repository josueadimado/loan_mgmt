# investors/admin.py
from django.contrib import admin
from .models import Investor, InvestorTransaction

@admin.register(Investor)
class InvestorAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'phone_number', 'funds_available', 'profit_earned', 'profit_paid', 'created_by', 'created_at']
    list_filter = ['region', 'currency', 'profit_paid', 'created_by']
    search_fields = ['first_name', 'last_name', 'phone_number', 'email']
    fields = [
        'first_name', 'last_name', 'phone_number', 'email', 'address', 'region',
        'id_document', 'currency', 'investment_period', 'funds_available',
        'profit_earned', 'profit_paid', 'profit_paid_date', 'last_profit_calculation',
        'created_by', 'created_at'
    ]

@admin.register(InvestorTransaction)
class InvestorTransactionAdmin(admin.ModelAdmin):
    list_display = ['investor', 'transaction_type', 'amount', 'date', 'created_by']
    list_filter = ['transaction_type', 'created_by']
    search_fields = ['investor__first_name', 'investor__last_name']