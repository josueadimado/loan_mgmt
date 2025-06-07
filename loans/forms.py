from django import forms
from .models import Loan

class LoanForm(forms.ModelForm):
    additional_principal = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        min_value=0,
        label="Additional Principal",
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Enter additional principal to add to the loan (optional)."
    )

    class Meta:
        model = Loan
        fields = [
            'borrower', 'product', 'principal', 'currency', 'interest_rate',
            'term_months', 'start_date', 'is_rollover', 'description'
        ]
        widgets = {
            'borrower': forms.Select(attrs={'class': 'form-select'}),
            'product': forms.Select(attrs={'class': 'selectpicker', 'data-live-search': 'true'}),
            'principal': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'term_months': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_rollover': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }