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
                'placeholder': 'e.g., 0598158589',
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
        required_fields = ['first_name', 'last_name', 'phone_number', 'id_doc_type', 'id_doc_number', 'id_doc_expiry']
        for name, field in self.fields.items():
            if name in required_fields:
                field.required = True
                field.widget.attrs['required'] = True
            else:
                field.required = False
                field.widget.attrs.pop('required', None)

    def clean_phone_number(self):
        phone_data = self.cleaned_data.get('phone_number', '')
        if not phone_data:
            raise forms.ValidationError("This field is required.")
        # Strip non-digit characters
        digits_only = ''.join(filter(str.isdigit, phone_data))
        if not digits_only or not (10 <= len(digits_only) <= 15):
            raise forms.ValidationError("Enter a valid phone number (10-15 digits, e.g., 0598158589). Non-digit characters (e.g., '+') are ignored.")
        return digits_only

    def clean_guarantor_phone(self):
        phone_data = self.cleaned_data.get('guarantor_phone', '')
        if phone_data:
            # Strip non-digit characters
            digits_only = ''.join(filter(str.isdigit, phone_data))
            if not digits_only or not (10 <= len(digits_only) <= 15):
                raise forms.ValidationError("Enter a valid phone number (10-15 digits, e.g., 0598158589). Non-digit characters (e.g., '+') are ignored.")
            return digits_only
        return None

    def save(self, commit=True):
        borrower = super().save(commit=False)
        if commit:
            borrower.save()
        # Handle additional_docs by creating BorrowerDocument instances
        for f in self.files.getlist('additional_docs'):
            BorrowerDocument.objects.create(borrower=borrower, document=f)
        return borrower