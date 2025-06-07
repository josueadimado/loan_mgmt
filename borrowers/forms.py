from django import forms
from django.forms import DateInput, Textarea, ClearableFileInput
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
import phonenumbers

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
    phone_number = PhoneNumberField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control phone-input',
                'placeholder': 'e.g., +233598158589',
                'data-country': 'gh',
            }
        ),
        label="Phone Number",
        region=None
    )
    guarantor_phone = PhoneNumberField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control phone-input',
                'placeholder': 'e.g., +233598158589',
                'data-country': 'gh',
            }
        ),
        label="Guarantor Phone",
        region=None
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

        # If we’re editing an existing borrower, prefill the phone inputs
        if self.instance and self.instance.pk:
            if self.instance.phone_number:
                self.fields['phone_number'].initial = self.instance.phone_number.as_e164
            if self.instance.guarantor_phone:
                self.fields['guarantor_phone'].initial = self.instance.guarantor_phone.as_e164

        # Always-required fields (except uploads & phones when present)
        always = [
            'first_name', 'last_name', 'email', 'address', 'region',
            'id_doc_type', 'id_doc_number', 'id_doc_expiry',
            'guarantor_name', 'guarantor_relationship', 'guarantor_address',
        ]
        for name in always:
            fld = self.fields[name]
            fld.required = True
            fld.widget.attrs['required'] = True

        # Make phone fields required only if they’re blank
        for ph in ('phone_number', 'guarantor_phone'):
            fld = self.fields[ph]
            has = bool(getattr(self.instance, ph, None))
            fld.required = not has
            if not has:
                fld.widget.attrs['required'] = True
            else:
                fld.widget.attrs.pop('required', None)

        # Make filefields required only if blank
        for ff in ('id_doc_file', 'guarantor_id_file'):
            fld = self.fields[ff]
            has = bool(getattr(self.instance, ff, None))
            fld.required = not has
            if not has:
                fld.widget.attrs['required'] = True
            else:
                fld.widget.attrs.pop('required', None)

    def clean_phone_number(self):
        phone_data = self.data.get('phone_number', '')
        original_phone_data = self.data.get('original_phone_number', '')
        print("Cleaning phone_number - Submitted value:", phone_data)
        print("Cleaning phone_number - Original submitted value:", original_phone_data)

        # Skip validation if the field hasn't changed (edit mode)
        if self.instance and self.instance.phone_number:
            original_value = self.instance.phone_number.as_e164
            print("Cleaning phone_number - Original database value:", original_value)
            if original_phone_data and phone_data == original_phone_data:
                print("Phone number unchanged (matches original submitted value), preserving original:", original_value)
                return self.instance.phone_number
            if not original_phone_data:
                original_phone_data = original_value
            normalized_phone_data = phone_data.replace('+', '').replace(' ', '')
            normalized_original = original_value.replace('+', '').replace(' ', '')
            if normalized_phone_data == normalized_original:
                print("Phone number unchanged (normalized match with database value), preserving original:", original_value)
                return self.instance.phone_number

        # Allow empty values if the field isn't required
        if not phone_data:
            if not self.fields['phone_number'].required:
                print("Phone number empty and not required, returning None")
                return None
            raise forms.ValidationError("This field is required.")

        try:
            parsed_number = phonenumbers.parse(phone_data)
            # Check if the number is possible
            if not phonenumbers.is_possible_number(parsed_number):
                raise forms.ValidationError("Enter a possible phone number (e.g., +233511287583).")
            # Check if the number is valid for the region
            if not phonenumbers.is_valid_number(parsed_number):
                raise forms.ValidationError("Enter a valid phone number for the selected country (e.g., +233511287583 for Ghana).")
            return PhoneNumber.from_string(phone_data)
        except phonenumbers.NumberParseException as e:
            raise forms.ValidationError(f"Enter a valid phone number (e.g., +233511287583): {str(e)}")

    def clean_guarantor_phone(self):
        phone_data = self.data.get('guarantor_phone', '')
        original_phone_data = self.data.get('original_guarantor_phone', '')
        print("Cleaning guarantor_phone - Submitted value:", phone_data)
        print("Cleaning guarantor_phone - Original submitted value:", original_phone_data)

        # Skip validation if the field hasn't changed (edit mode)
        if self.instance and self.instance.guarantor_phone:
            original_value = self.instance.guarantor_phone.as_e164
            print("Cleaning guarantor_phone - Original database value:", original_value)
            if original_phone_data and phone_data == original_phone_data:
                print("Guarantor phone unchanged (matches original submitted value), preserving original:", original_value)
                return self.instance.guarantor_phone
            if not original_phone_data:
                original_phone_data = original_value
            normalized_phone_data = phone_data.replace('+', '').replace(' ', '')
            normalized_original = original_value.replace('+', '').replace(' ', '')
            if normalized_phone_data == normalized_original:
                print("Guarantor phone unchanged (normalized match with database value), preserving original:", original_value)
                return self.instance.guarantor_phone

        # Allow empty values if the field isn't required
        if not phone_data:
            if not self.fields['guarantor_phone'].required:
                print("Guarantor phone empty and not required, returning None")
                return None
            raise forms.ValidationError("This field is required.")

        try:
            parsed_number = phonenumbers.parse(phone_data)
            # Check if the number is possible
            if not phonenumbers.is_possible_number(parsed_number):
                raise forms.ValidationError("Enter a possible phone number (e.g., +233511287583).")
            # Check if the number is valid for the region
            if not phonenumbers.is_valid_number(parsed_number):
                raise forms.ValidationError("Enter a valid phone number for the selected country (e.g., +233511287583 for Ghana).")
            return PhoneNumber.from_string(phone_data)
        except phonenumbers.NumberParseException as e:
            raise forms.ValidationError(f"Enter a valid phone number (e.g., +233511287583): {str(e)}")

    def save(self, commit=True):
        borrower = super().save(commit=False)
        # Handle phone numbers: if None, don't update the field
        if 'phone_number' in self.cleaned_data and self.cleaned_data['phone_number'] is None:
            del self.cleaned_data['phone_number']
        if 'guarantor_phone' in self.cleaned_data and self.cleaned_data['guarantor_phone'] is None:
            del self.cleaned_data['guarantor_phone']

        # Set attributes on the borrower instance, excluding additional_docs
        for field, value in self.cleaned_data.items():
            if field != 'additional_docs':
                setattr(borrower, field, value)

        if commit:
            borrower.save()

        # Handle additional_docs by creating BorrowerDocument instances
        for f in self.files.getlist('additional_docs'):
            BorrowerDocument.objects.create(borrower=borrower, document=f)

        return borrower