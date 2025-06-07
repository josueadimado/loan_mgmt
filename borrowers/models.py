# borrowers/models.py

from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField

class Borrower(models.Model):
    REGION_CHOICES = [
        ('Greater Accra', 'Greater Accra'),
        ('Ashanti',       'Ashanti'),
        ('Northern',      'Northern'),
        ('Upper East',    'Upper East'),
        ('Upper West',    'Upper West'),
        ('Volta',         'Volta'),
        ('Eastern',       'Eastern'),
        ('Western',       'Western'),
        ('Central',       'Central'),
        ('Bono',          'Bono'),
        ('Bono East',     'Bono East'),
        ('Ahafo',         'Ahafo'),
        ('Savannah',      'Savannah'),
        ('North East',    'North East'),
        ('Oti',           'Oti'),
        ('Western North', 'Western North'),
    ]

    ID_TYPE_CHOICES = [
        ('nid',   'National ID Card'),
        ('pp',    'Passport'),
        ('voter', 'Voter ID'),
    ]

    # --- Personal Information ---
    first_name   = models.CharField(max_length=50, null=True, blank=True)
    last_name    = models.CharField(max_length=50, null=True, blank=True)
    phone_number = PhoneNumberField(region="GH", null=True, blank=True)
    email        = models.EmailField(null=True, blank=True)
    address      = models.CharField(max_length=255, null=True, blank=True)
    region       = models.CharField(
        max_length=20,
        choices=REGION_CHOICES,
        verbose_name="Region",
        null=True,
        blank=True
    )

    # --- Customer Identification ---
    id_doc_type   = models.CharField(
        max_length=10,
        choices=ID_TYPE_CHOICES,
        null=True,
        blank=True
    )
    id_doc_number = models.CharField(max_length=100, null=True, blank=True)
    id_doc_expiry = models.DateField(null=True, blank=True)
    id_doc_file   = models.FileField(
        upload_to='borrowers/id_docs/',
        null=True,
        blank=True
    )

    # --- Guarantor Information ---
    guarantor_name         = models.CharField(max_length=100, null=True, blank=True)
    guarantor_relationship = models.CharField(max_length=100, null=True, blank=True)
    guarantor_phone        = PhoneNumberField(region="GH", null=True, blank=True)
    guarantor_address      = models.CharField(max_length=255, null=True, blank=True)

    # --- Guarantor Identification ---
    guarantor_id_type   = models.CharField(
        max_length=10,
        choices=ID_TYPE_CHOICES,
        null=True,
        blank=True
    )
    guarantor_id_number = models.CharField(max_length=100, null=True, blank=True)
    guarantor_id_expiry = models.DateField(null=True, blank=True)
    guarantor_id_file   = models.FileField(
        upload_to='borrowers/guarantor_id_docs/',
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
        verbose_name="Created At"
    )

    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()


class BorrowerDocument(models.Model):
    borrower    = models.ForeignKey(
        Borrower,
        on_delete=models.CASCADE,
        related_name='additional_docs'
    )
    document    = models.FileField(upload_to='borrowers/additional_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.borrower}"