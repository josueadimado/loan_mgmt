# users/urls.py
from django.urls import path
from .views import user_settings

app_name = 'users'

urlpatterns = [
    path('settings/', user_settings, name='settings'),
]