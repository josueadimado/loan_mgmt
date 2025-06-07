# exchange_rates/forms.py
from django import forms
from .models import ExchangeRate
from decimal import Decimal

class ExchangeRateForm(forms.ModelForm):
    class Meta:
        model = ExchangeRate
        fields = ['rate']
        widgets = {
            'rate': forms.NumberInput(attrs={'step': '0.0001', 'min': '0', 'class': 'form-control'}),
        }
        labels = {
            'rate': 'USD to GHS Exchange Rate',
        }

    def clean_rate(self):
        rate = self.cleaned_data.get('rate')
        if rate <= 0:
            raise forms.ValidationError("The exchange rate must be greater than 0.")
        return rate