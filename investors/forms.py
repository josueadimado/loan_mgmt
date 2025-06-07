# investors/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import Investor, InvestorTransaction

User = get_user_model()

class InvestorForm(forms.ModelForm):
    initial_investment = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        label="Initial Investment Amount",
        help_text="Enter the initial amount the investor is investing (optional)."
    )

    class Meta:
        model = Investor
        fields = [
            'first_name', 'last_name',
            'phone_number', 'email',
            'address', 'region',
            'id_document',
            'currency', 'investment_period',
            'funds_available',
            'created_at',  # Added to set the join/first investment date
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'phone-input'}),
            'region': forms.Select(),
            'address': forms.Textarea(attrs={'rows': 3}),
            'id_document': forms.FileInput(),
            'investment_period': forms.NumberInput(attrs={'min': 3}),
            'created_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Get the current user from the view
        super().__init__(*args, **kwargs)
        # Make funds_available read-only (managed via transactions)
        self.fields['funds_available'].disabled = True
        self.fields['funds_available'].help_text = "This field is updated via transactions."

    def clean_investment_period(self):
        investment_period = self.cleaned_data.get('investment_period')
        if investment_period is not None and investment_period < 3:
            raise forms.ValidationError("The minimum investment period is one quarter (3 months).")
        return investment_period

    def clean_initial_investment(self):
        initial_investment = self.cleaned_data.get('initial_investment')
        if initial_investment is not None and initial_investment < 0:
            raise forms.ValidationError("Initial investment cannot be negative.")
        return initial_investment

    def clean_funds_available(self):
        funds_available = self.cleaned_data.get('funds_available')
        if funds_available is not None and funds_available < 0:
            raise forms.ValidationError("Funds available cannot be negative.")
        return funds_available

    def save(self, commit=True):
        investor = super().save(commit=False)
        if not investor.pk and self.user:  # If creating a new investor
            investor.created_by = self.user
        if commit:
            investor.save()
        return investor

class InvestorTransactionForm(forms.ModelForm):
    class Meta:
        model = InvestorTransaction
        fields = ['transaction_type', 'amount']
        widgets = {
            'transaction_type': forms.Select(choices=[
                ('topup', 'Top-Up'),  # Only allow top-up transactions
            ]),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.investor = kwargs.pop('investor', None)
        super().__init__(*args, **kwargs)
        # Restrict transaction_type to 'topup'
        self.fields['transaction_type'].choices = [('topup', 'Top-Up')]
        self.fields['amount'].label = "Top-Up Amount"
        self.fields['amount'].help_text = "Enter the amount to add to the investor's funds."

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Top-up amount must be positive.")
        return amount

    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.investor = self.investor
        transaction.created_by = self.user
        if commit:
            transaction.save()
        # Update investor's funds_available
        if transaction.transaction_type == 'topup':
            transaction.investor.funds_available += transaction.amount
            transaction.investor.save()
        return transaction