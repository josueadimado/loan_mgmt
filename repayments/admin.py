from django.contrib import admin
from .models import Repayment

@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    list_display = ['loan', 'date', 'amount', 'method']
    list_filter = ['method', 'date']
    search_fields = ['loan__id']