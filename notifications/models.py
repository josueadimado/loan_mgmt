from django.db import models

class SMSTemplate(models.Model):
    name         = models.CharField(max_length=100, unique=True)
    message_body = models.TextField(
        help_text="Use placeholders: {name}, {due_date}, {amount_due}"
    )

    def __str__(self):
        return self.name


class SMSLog(models.Model):
    to_number = models.CharField(max_length=15)
    template  = models.ForeignKey(SMSTemplate, on_delete=models.SET_NULL, null=True)
    sent_at   = models.DateTimeField(auto_now_add=True)
    status    = models.CharField(max_length=20)
    response  = models.TextField(blank=True)

    def __str__(self):
        return f"{self.to_number} @ {self.sent_at:%Y-%m-%d %H:%M}"