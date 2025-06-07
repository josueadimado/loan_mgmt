import datetime
import json
from dateutil.relativedelta import relativedelta
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
import csv
from decimal import Decimal

from .models import Loan  # Import Loan from models
from .forms import LoanForm
from repayments.models import Repayment
from borrowers.models import Borrower

class LoanListView(ListView):
    model = Loan
    template_name = 'loans/loan_list.html'
    context_object_name = 'loans'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset().select_related('borrower', 'product').prefetch_related('repayments')
        ctx['count'] = qs.count()

        loan_rows = []
        for loan in qs:
            total = loan.get_total_to_pay()
            due_date = loan.get_due_date()
            total_paid = sum(repayment.amount for repayment in loan.repayments.all())
            remaining = max(0, total - total_paid)
            loan_rows.append({
                'obj': loan,
                'borrower': f"{loan.borrower.first_name} {loan.borrower.last_name}",
                'principal': loan.principal,
                'total_to_pay': total,
                'total_paid': total_paid,
                'remaining': remaining,
                'currency': loan.currency,
                'interest_rate': loan.interest_rate,
                'status': loan.status,
                'due_date': due_date,
                'product_name': loan.product.name if loan.product else '-',
            })
        ctx['loans'] = loan_rows
        return ctx

class LoanCreateView(CreateView):
    model = Loan
    form_class = LoanForm
    template_name = 'loans/loan_form.html'
    success_url = reverse_lazy('loans:loan-list')

    def get_initial(self):
        initial = super().get_initial()
        borrower_pk = self.request.GET.get('borrower')
        if borrower_pk:
            initial['borrower'] = borrower_pk
        return initial

class LoanUpdateView(UpdateView):
    model = Loan
    form_class = LoanForm
    template_name = 'loans/loan_form.html'
    success_url = reverse_lazy('loans:loan-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['borrower'] = self.object.borrower
        return context

    def form_valid(self, form):
        additional_principal = form.cleaned_data.get('additional_principal')
        if additional_principal and additional_principal > 0:
            self.object.principal += Decimal(additional_principal)
            messages.info(self.request, f"Added {additional_principal} {self.object.currency} to the loan principal. New principal: {self.object.principal}")

        if form.cleaned_data['is_rollover'] and not self.object.is_rollover:
            self.object.rollover_count += 1
            self.object.is_rollover = True
            messages.info(self.request, f"Loan rolled over. Rollover count: {self.object.rollover_count}")

        changed = False
        changes = []

        for field in form.fields:
            if field == 'additional_principal':
                continue
            submitted_value = form.cleaned_data.get(field)
            existing_value = getattr(self.object, field)

            if field == 'borrower':
                submitted_value_str = str(submitted_value.id) if submitted_value else ''
                existing_value_str = str(existing_value.id) if existing_value else ''
                if submitted_value_str != existing_value_str:
                    changes.append(f"{field}: submitted={submitted_value}, existing={existing_value}")
                    changed = True
            elif field == 'product':
                submitted_value_id = str(submitted_value.id) if submitted_value else ''
                existing_value_id = str(existing_value.id) if existing_value else ''
                if submitted_value_id != existing_value_id:
                    changes.append(f"{field}: submitted={submitted_value}, existing={existing_value}")
                    changed = True
            else:
                if field == 'start_date':
                    submitted_str = str(submitted_value) if submitted_value else ''
                    existing_str = str(existing_value) if existing_value else ''
                    if submitted_str != existing_str:
                        changes.append(f"{field}: submitted={submitted_value}, existing={existing_value}")
                        changed = True
                else:
                    if submitted_value != existing_value:
                        changes.append(f"{field}: submitted={submitted_value}, existing={existing_value}")
                        changed = True

        if changes:
            print("Changes detected:", changes)
        else:
            print("No changes detected.")

        if not changed and not form.cleaned_data['is_rollover'] and not (additional_principal and additional_principal > 0):
            messages.info(self.request, "Nothing changed.")
            return super().form_valid(form)

        response = super().form_valid(form)
        messages.success(self.request, "Loan updated successfully.")
        return response

    def form_invalid(self, form):
        print("Form is invalid. Errors:", form.errors)
        print("POST data:", self.request.POST)
        return super().form_invalid(form)

class LoanDetailView(DetailView):
    model = Loan
    template_name = 'loans/loan_detail.html'
    context_object_name = 'loan'

    def get_queryset(self):
        return Loan.objects.prefetch_related('repayments').select_related('borrower', 'product')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        loan = self.object

        print(f"Loan #{loan.id} details: Status={loan.status}, Total Paid={loan.get_total_paid()}, Remaining={loan.get_remaining_amount_to_pay()}")

        monthly_interest = loan.get_monthly_interest_payment()
        schedule = []
        total_term = loan.original_term_months + (loan.rollover_count * loan.original_term_months)
        for m in range(1, total_term + 1):
            item_due = loan.start_date + relativedelta(months=m)
            schedule.append({
                'month': m,
                'interest': monthly_interest,
                'is_last': (m == total_term),
                'due_date': item_due,
            })

        ctx.update({
            'due_date': loan.get_due_date(),
            'schedule': schedule,
            'rollover_count': loan.rollover_count,
        })
        return ctx

class LoanExportView(View):
    def get(self, request, *args, **kwargs):
        qs = Loan.objects.select_related('borrower', 'product').prefetch_related('repayments')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="loans.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Borrower', 'Principal', 'Total To Pay', 'Amount Paid', 'Remaining',
            'Currency', 'Rate%', 'Status', 'Due Date', 'Loan Type'
        ])
        for loan in qs:
            total = loan.get_total_to_pay()
            total_paid = sum(repayment.amount for repayment in loan.repayments.all())
            remaining = max(0, total - total_paid)
            due = loan.get_due_date()
            writer.writerow([
                f"{loan.borrower.first_name} {loan.borrower.last_name}",
                f"{loan.principal:.2f} {loan.currency}",
                f"{total:.2f} {loan.currency}",
                f"{total_paid:.2f} {loan.currency}",
                f"{remaining:.2f} {loan.currency}",
                loan.currency,
                f"{loan.interest_rate}%",
                loan.status,
                due.strftime('%Y-m-d'),
                loan.product.name if loan.product else '-',
            ])
        return response

class LoanHistoryView(DetailView):
    model = Loan
    template_name = 'loans/loan_history.html'
    context_object_name = 'loan'

    def get_queryset(self):
        return Loan.objects.prefetch_related('repayments').select_related('borrower', 'product')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        loan = self.object

        repayments = loan.repayments.all()
        total_to_pay = loan.get_total_to_pay()
        total_paid = sum(repayment.amount for repayment in repayments)
        remaining_balance = max(0, total_to_pay - total_paid)

        ctx.update({
            'repayments': repayments,
            'total_to_pay': total_to_pay,
            'total_paid': total_paid,
            'remaining_balance': remaining_balance,
            'due_date': loan.get_due_date(),
            'current_date': datetime.datetime.now(),
        })
        return ctx

class BorrowerSearchView(View):
    def get(self, request, *args, **kwargs):
        loan_id = request.GET.get('loan_id', '')
        if loan_id:
            try:
                loan = Loan.objects.get(id=loan_id)
                borrower_name = f"{loan.borrower.first_name} {loan.borrower.last_name}"
                return JsonResponse({'borrower_name': borrower_name}, safe=False)
            except Loan.DoesNotExist:
                return JsonResponse({'borrower_name': ''}, safe=False)

        query = request.GET.get('q', '')
        if not query or len(query) < 2:
            return JsonResponse([], safe=False)

        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse(status=400)

        borrowers = Borrower.objects.filter(
            first_name__icontains=query
        ) | Borrower.objects.filter(
            last_name__icontains=query
        )
        borrowers = borrowers[:10]

        results = [
            {
                'id': borrower.id,
                'first_name': borrower.first_name,
                'last_name': borrower.last_name,
            }
            for borrower in borrowers
        ]
        return JsonResponse(results, safe=False)