from django import forms
from django.forms import DateInput, Textarea, ClearableFileInput
from .models import Borrower, BorrowerDocument

class MultiFileInput(ClearableFileInput):
    """Custom widget to support selecting multiple files."""
    allow_multiple_selected = True
    def __init__(self, attrs=None):
        attrs = {} if attrs is None else attrs.copy()
        attrs.pop('multiple', None)
        super().__init__(attrs)
        self.attrs['multiple'] = True

class BorrowerForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '233XXXXXXXXX',
                'inputmode': 'numeric',
                'pattern': '\\d*',
            }
        ),
        label="Phone Number"
    )
    guarantor_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 0598158589',
            }
        ),
        label="Guarantor Phone"
    )
    additional_docs = forms.FileField(
        widget=MultiFileInput(),
        required=False,
        label="Additional Documents"
    )

    class Meta:
        model = Borrower
        fields = [
            'first_name', 'last_name', 'phone_number', 'email', 'address', 'region',
            'id_doc_type', 'id_doc_number', 'id_doc_expiry', 'id_doc_file',
            'guarantor_name', 'guarantor_relationship', 'guarantor_phone', 'guarantor_address',
            'guarantor_id_type', 'guarantor_id_number', 'guarantor_id_expiry', 'guarantor_id_file',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'region': forms.Select(attrs={'class': 'form-select'}),
            'id_doc_type': forms.Select(attrs={'class': 'form-select'}),
            'id_doc_number': forms.TextInput(attrs={'class': 'form-control'}),
            'id_doc_expiry': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'id_doc_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'guarantor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'guarantor_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'guarantor_address': Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'guarantor_id_type': forms.Select(attrs={'class': 'form-select'}),
            'guarantor_id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'guarantor_id_expiry': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'guarantor_id_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required fields explicitly
        # Make ID fields optional per request
        required_fields = ['first_name', 'last_name', 'phone_number']
        for name, field in self.fields.items():
            if name in required_fields:
                field.required = True
                field.widget.attrs['required'] = True
            else:
                field.required = False
                field.widget.attrs.pop('required', None)
        # Prefill Ghana country code for new/empty forms only
        if not self.is_bound and (not getattr(self.instance, 'phone_number', None)):
            self.fields['phone_number'].initial = '233'

    @staticmethod
    def _normalize_ghana_phone(raw: str) -> str:
        digits = ''.join(filter(str.isdigit, raw or ''))
        if not digits:
            return ''
        # Cases:
        # 1) 0XXXXXXXXX (10 digits local) -> 233 + 9 digits
        if len(digits) == 10 and digits.startswith('0'):
            return '233' + digits[1:]
        # 2) 233XXXXXXXXX (12 digits intl) -> keep
        if len(digits) == 12 and digits.startswith('233'):
            return digits
        # 3) 9 digits (missing leading 0) -> assume mobile local -> 233 + 9
        if len(digits) == 9 and not digits.startswith('0') and not digits.startswith('233'):
            return '233' + digits
        # 4) 2330XXXXXXXX (13 digits) -> sometimes entered with 0 after 233
        if len(digits) == 13 and digits.startswith('2330'):
            return '233' + digits[4:]
        # Otherwise invalid for our simplified rules
        raise forms.ValidationError("Enter a valid Ghana number. Use 233XXXXXXXXX or 0XXXXXXXXX.")

    def clean_phone_number(self):
        phone_data = self.cleaned_data.get('phone_number', '')
        if not phone_data:
            raise forms.ValidationError("This field is required.")
        normalized = self._normalize_ghana_phone(phone_data)
        if not normalized:
            raise forms.ValidationError("Enter a valid Ghana number.")
        return normalized

    def clean_guarantor_phone(self):
        phone_data = self.cleaned_data.get('guarantor_phone', '')
        if phone_data:
            return self._normalize_ghana_phone(phone_data)
        return None

    def save(self, commit=True):
        borrower = super().save(commit=False)
        if commit:
            borrower.save()
        # Handle additional_docs by creating BorrowerDocument instances
        for f in self.files.getlist('additional_docs'):
            BorrowerDocument.objects.create(borrower=borrower, document=f)
        return borrower


class BulkBorrowerUploadForm(forms.Form):
    file = forms.FileField(
        label="CSV File",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )
    help_text = "CSV columns: first_name,last_name,phone_number,email,address,region"