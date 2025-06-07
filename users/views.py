# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordResetCompleteView
from .forms import UserUpdateForm, CustomPasswordChangeForm

@login_required
def user_settings(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if 'update_details' in request.POST:
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Your profile has been updated successfully.")
                return redirect('users:settings')
            else:
                messages.error(request, "Please correct the errors below.")

        elif 'change_password' in request.POST:
            if password_form.is_valid():
                password_form.save()
                messages.success(request, "Your password has been changed successfully. Please log in again.")
                return redirect('login')
            else:
                messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user)

    context = {
        'user_form': user_form,
        'password_form': password_form,
    }
    return render(request, 'users/settings.html', context)

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'

    def get(self, request, *args, **kwargs):
        print("Rendering Password Reset Complete page")
        return super().get(request, *args, **kwargs)