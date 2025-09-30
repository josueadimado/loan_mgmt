from django.urls import path
from .views import (
    LoanListView,
    LoanCreateView,
    LoanUpdateView,
    LoanDetailView,
    LoanExportView,
    LoanHistoryView,
    BorrowerSearchView,
    LoanBulkUploadView,
    LoanBulkTemplateCSVView,
    LoanBulkExportCSVView,
)

app_name = 'loans'

urlpatterns = [
    path('',                LoanListView.as_view(),    name='loan-list'),
    path('create/',         LoanCreateView.as_view(),  name='loan-create'),
    path('<int:pk>/',       LoanDetailView.as_view(),  name='loan-detail'),
    path('<int:pk>/edit/',  LoanUpdateView.as_view(),  name='loan-update'),
    path('export/',         LoanExportView.as_view(),  name='loan-export'),
    path('bulk-upload/',    LoanBulkUploadView.as_view(), name='loan-bulk-upload'),
    path('bulk-upload/template.csv', LoanBulkTemplateCSVView.as_view(), name='loan-bulk-template'),
    path('bulk-upload/export.csv',   LoanBulkExportCSVView.as_view(),   name='loan-bulk-export'),
    path('<int:pk>/history/', LoanHistoryView.as_view(), name='loan-history'),
    path('borrowers/search/', BorrowerSearchView.as_view(), name='borrower-search'),
]