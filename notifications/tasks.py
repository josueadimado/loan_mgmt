# notifications/tasks.py
from celery import shared_task
from django.utils import timezone
from twilio.rest import Client
from django.conf import settings
from .models import SMSTemplate, SMSLog
from repayments.models import RepaymentSchedule

@shared_task
def send_due_sms(reminder_days=1):
    today = timezone.now().date()
    target_date = today + timezone.timedelta(days=reminder_days)
    schedules = RepaymentSchedule.objects.filter(due_date=target_date, status='due')
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    try:
        template = SMSTemplate.objects.get(name='Payment Reminder')
    except SMSTemplate.DoesNotExist:
        print("Error: SMSTemplate 'Payment Reminder' does not exist.")
        return

    for sched in schedules:
        # Ensure borrower has a valid phone number
        phone_number = str(sched.loan.borrower.phone_number)
        if not phone_number.startswith('+'):
            print(f"Invalid phone number format for {sched.loan.borrower}: {phone_number}")
            continue

        # Safely access borrower name
        borrower_name = getattr(sched.loan.borrower, 'name', 'Customer')

        msg_body = template.message_body.format(
            name=borrower_name,
            due_date=sched.due_date,
            amount_due=sched.amount_due
        )
        try:
            resp = client.messages.create(
                body=msg_body,
                from_=settings.TWILIO_FROM_NUMBER,
                to=phone_number
            )
            status = 'sent'
            response = resp.sid
        except Exception as e:
            status = 'failed'
            response = str(e)
            print(f"Failed to send SMS to {phone_number}: {e}")

        SMSLog.objects.create(
            to_number=phone_number,
            template=template,
            status=status,
            response=response
        )