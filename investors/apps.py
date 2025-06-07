# investors/apps.py
from django.apps import AppConfig

class InvestorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'investors'

    def ready(self):
        from django_celery_beat.models import PeriodicTask, CrontabSchedule
        # Create a schedule (e.g., run daily at midnight)
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='0',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )
        # Create the periodic task
        PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name='Pay Investor Earnings',
            task='investors.tasks.pay_investor_earnings',
            defaults={'enabled': True},
        )