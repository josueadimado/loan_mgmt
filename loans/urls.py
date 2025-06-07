from django.urls import path
from .views import (
    LoanListView,
    LoanCreateView,
    LoanUpdateView,
    LoanDetailView,
    LoanExportView,
    LoanHistoryView,
    BorrowerSearchView,
)

app_name = 'loans'

urlpatterns = [
    path('',                LoanListView.as_view(),    name='loan-list'),
    path('create/',         LoanCreateView.as_view(),  name='loan-create'),
    path('<int:pk>/',       LoanDetailView.as_view(),  name='loan-detail'),
    path('<int:pk>/edit/',  LoanUpdateView.as_view(),  name='loan-update'),
    path('export/',         LoanExportView.as_view(),  name='loan-export'),
    path('<int:pk>/history/', LoanHistoryView.as_view(), name='loan-history'),
    path('borrowers/search/', BorrowerSearchView.as_view(), name='borrower-search'),
]