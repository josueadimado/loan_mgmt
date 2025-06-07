from django.contrib import admin
from .models import SMSTemplate, SMSLog

@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    list_display  = ('name',)
    search_fields = ('name',)


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display  = ('to_number', 'template', 'sent_at', 'status')
    list_filter   = ('status', 'sent_at')
    search_fields = ('to_number',)