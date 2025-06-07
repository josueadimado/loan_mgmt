from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Repayment
from .forms import RepaymentForm
from django.utils.dateparse import parse_date

class RepaymentListView(ListView):
    model = Repayment
    template_name = 'repayments/repayment_list.html'
    context_object_name = 'repayments'

    def get_queryset(self):
        qs = super().get_queryset().select_related('loan__borrower', 'loan__product')
        # Apply date range filter if provided
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                qs = qs.filter(date__gte=start_date)
        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                qs = qs.filter(date__lte=end_date)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx['count'] = qs.count()
        # Pass the current filter values to the template
        ctx['start_date'] = self.request.GET.get('start_date', '')
        ctx['end_date'] = self.request.GET.get('end_date', '')
        return ctx


class RepaymentCreateView(CreateView):
    model = Repayment
    form_class = RepaymentForm
    template_name = 'repayments/repayment_form.html'
    success_url = reverse_lazy('repayments:repayment-list')

    def get_initial(self):
        initial = super().get_initial()
        loan_id = self.request.GET.get('loan_id')
        if loan_id:
            try:
                initial['loan'] = loan_id
            except ValueError:
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loan_id = self.request.GET.get('loan_id')
        if loan_id:
            try:
                from loans.models import Loan  # Import here to avoid circular imports
                loan = Loan.objects.get(id=loan_id)
                context['selected_borrower'] = f"{loan.borrower.first_name} {loan.borrower.last_name}"
            except Loan.DoesNotExist:
                pass
        return context

    def form_valid(self, form):
        # Save the repayment
        response = super().form_valid(form)
        # Update the associated loan's status
        loan = self.object.loan
        loan.update_status()
        loan.save()
        messages.success(self.request, f"Repayment of {self.object.amount} {loan.currency} recorded for Loan #{loan.id}.")
        return response