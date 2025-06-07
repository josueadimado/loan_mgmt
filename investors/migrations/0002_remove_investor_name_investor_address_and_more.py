# investors/migrations/0002_remove_investor_name_investor_address_and_more.py
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields
import django.utils.timezone
from django.conf import settings  # Add this import

def migrate_name_to_first_last(apps, schema_editor):
    Investor = apps.get_model('investors', 'Investor')
    for investor in Investor.objects.all():
        if investor.name:
            parts = investor.name.split(maxsplit=1)
            investor.first_name = parts[0]
            investor.last_name = parts[1] if len(parts) > 1 else ""
            investor.save()

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('investors', '0001_initial'),
    ]

    operations = [
        # Add first_name and last_name with temporary defaults
        migrations.AddField(
            model_name='Investor',
            name='first_name',
            field=models.CharField(default='Unknown', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='Investor',
            name='last_name',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        # Migrate data from name to first_name and last_name
        migrations.RunPython(
            migrate_name_to_first_last,
            reverse_code=migrations.RunPython.noop,
        ),
        # Remove the name field
        migrations.RemoveField(
            model_name='Investor',
            name='name',
        ),
        migrations.AddField(
            model_name='Investor',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='Investor',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='Investor',
            name='currency',
            field=models.CharField(choices=[('GHS', 'Cedis (GHS)'), ('USD', 'Dollars (USD)')], default='GHS', max_length=3),
        ),
        migrations.AddField(
            model_name='Investor',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='Investor',
            name='region',
            field=models.CharField(blank=True, choices=[('CR', 'Central Region'), ('ER', 'Eastern Region'), ('GR', 'Greater Accra Region'), ('NR', 'Northern Region'), ('WR', 'Western Region')], max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='Investor',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(default='', max_length=128, region=None),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='InvestorTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('deposit', 'Initial Deposit'), ('topup', 'Top-Up'), ('withdrawal', 'Withdrawal'), ('return', 'Return Payment')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('investor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='investors.investor')),
            ],
        ),
    ]