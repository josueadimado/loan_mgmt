# borrowers/admin.py

from django.contrib import admin
from .models import Borrower, BorrowerDocument

@admin.register(Borrower)
class BorrowerAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'phone_number',
        'email', 'region', 'created_at',
    )
    list_filter = (
        'region',
        'id_doc_type',
        'guarantor_id_type',
    )
    search_fields = (
        'first_name',
        'last_name',
        'phone_number',
        'email',
    )
    readonly_fields = ('created_at',)

@admin.register(BorrowerDocument)
class BorrowerDocumentAdmin(admin.ModelAdmin):
    list_display  = ('borrower', 'document', 'uploaded_at')
    list_filter   = ('borrower',)
    search_fields = (
        'borrower__first_name',
        'borrower__last_name',
    )
    readonly_fields = ('uploaded_at',)