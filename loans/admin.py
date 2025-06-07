from django.contrib import admin
from .models import Loan, LoanProduct

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['id', 'borrower', 'product', 'principal', 'currency', 'interest_rate', 'start_date', 'status']
    list_filter = ['currency', 'status', 'start_date']
    search_fields = ['borrower__first_name', 'borrower__last_name']

@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']