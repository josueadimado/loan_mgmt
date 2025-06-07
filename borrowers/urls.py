from django.urls import path
from .views import (
    BorrowerListView,
    BorrowerCreateView,
    BorrowerUpdateView,
    BorrowerDetailView,
    BorrowerExportView,
    BorrowerStatementView,  # Add the new view
)

app_name = 'borrowers'

urlpatterns = [
    path('', BorrowerListView.as_view(), name='borrower-list'),
    path('create/', BorrowerCreateView.as_view(), name='borrower-create'),
    path('<int:pk>/', BorrowerDetailView.as_view(), name='borrower-detail'),
    path('<int:pk>/edit/', BorrowerUpdateView.as_view(), name='borrower-update'),
    path('export/', BorrowerExportView.as_view(), name='borrower-export'),
    path('<int:pk>/statement/', BorrowerStatementView.as_view(), name='borrower-statement'),  # New URL
]