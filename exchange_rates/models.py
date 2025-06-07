from django.db import models
from django.utils import timezone
from decimal import Decimal

class ExchangeRate(models.Model):
    from_currency = models.CharField(max_length=3, default='USD')
    to_currency = models.CharField(max_length=3, default='GHS')
    rate = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('15.0000'))
    last_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Exchange Rate"
        verbose_name_plural = "Exchange Rates"

    def __str__(self):
        return f"{self.from_currency} to {self.to_currency}: {self.rate} (Last Updated: {self.last_updated})"

    @classmethod
    def get_usd_to_ghs_rate(cls):
        rate_obj, created = cls.objects.get_or_create(
            from_currency='USD',
            to_currency='GHS',
            defaults={'rate': Decimal('15.0000'), 'last_updated': timezone.now()}
        )
        return rate_obj.rate