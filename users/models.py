# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('officer', 'Loan Officer'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='officer',
        help_text='Designates whether this user is an admin or loan officer.'
    )
    phone_number = PhoneNumberField(
        blank=True,
        null=True,
        unique=True,
        help_text="Phone number in international format (e.g., +233123456789)."
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"