from django import forms
from .models import Repayment
from loans.models import Loan

class RepaymentForm(forms.ModelForm):
    class Meta:
        model = Repayment
        fields = ['loan', 'date', 'amount', 'method']
        widgets = {
            'loan': forms.Select(attrs={'class': 'selectpicker', 'data-live-search': 'true'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'method': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter loans to only show active loans
        self.fields['loan'].queryset = Loan.objects.filter(status='active').select_related('borrower')
        # Customize the display of loans in the dropdown
        self.fields['loan'].label_from_instance = lambda obj: f"Loan #{obj.id} - {obj.borrower.first_name} {obj.borrower.last_name}"