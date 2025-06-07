from django.urls import path
from .views import RepaymentListView, RepaymentCreateView

app_name = 'repayments'

urlpatterns = [
    path('', RepaymentListView.as_view(), name='repayment-list'),
    path('create/', RepaymentCreateView.as_view(), name='repayment-create'),
]