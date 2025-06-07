# loan_mgmt/tasks.py
from celery import shared_task
from django.core.management import call_command

@shared_task
def calculate_investor_profits():
    call_command('calculate_investor_profits')