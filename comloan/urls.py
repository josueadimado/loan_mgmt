"""
URL configuration for comloan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# loan_mgmt/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import dashboard

# from django.conf import settings
# from django.conf.urls.static import static

urlpatterns = [
    # Auth (login/logout)
    path('accounts/', include('django.contrib.auth.urls')),

    # Custom Password Reset URLs
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'
    ), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Admin
    path('admin/', admin.site.urls),

    # Root dashboard
    path('', dashboard, name='dashboard'),
    # Add pattern for /dashboard/
    path('dashboard/', dashboard, name='dashboard_alt'),

    # Namespaced app URLs
    path('borrowers/', include(('borrowers.urls', 'borrowers'), namespace='borrowers')),
    path('investors/', include(('investors.urls', 'investors'), namespace='investors')),
    path('loans/', include(('loans.urls', 'loans'), namespace='loans')),
    path('repayments/', include(('repayments.urls', 'repayments'), namespace='repayments')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
]

# if settings.DEBUG:
#     # Serve static files
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
#     # Serve media/uploads
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
