from django.db import migrations

def add_loan_products(apps, schema_editor):
    LoanProduct = apps.get_model('loans', 'LoanProduct')
    loan_types = [
        'Business Loan',
        'Personal Loan',
        'Education Loan',
        'Mortgage Loan',
    ]
    for name in loan_types:
        LoanProduct.objects.get_or_create(name=name)

def remove_loan_products(apps, schema_editor):
    LoanProduct = apps.get_model('loans', 'LoanProduct')
    LoanProduct.objects.filter(name__in=[
        'Business Loan',
        'Personal Loan',
        'Education Loan',
        'Mortgage Loan',
    ]).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('loans', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_loan_products, remove_loan_products),
    ]