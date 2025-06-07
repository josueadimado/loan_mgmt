from django.core.management.base import BaseCommand
from investors.models import Investor

class Command(BaseCommand):
    help = 'Calculate quarterly profits for all investors'

    def handle(self, *args, **options):
        investors = Investor.objects.all()
        for investor in investors:
            profit = investor.calculate_quarterly_profit()
            if profit > 0:
                self.stdout.write(self.style.SUCCESS(
                    f'Calculated {profit} GHS profit for {investor}'
                ))
        self.stdout.write(self.style.SUCCESS('Profit calculation complete.'))