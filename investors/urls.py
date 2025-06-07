# investors/urls.py
from django.urls import path
from .views import (
    InvestorListView,
    InvestorUpdateView,
    InvestorDetailView,
    InvestorExportView,
)

app_name = 'investors'

urlpatterns = [
    path('', InvestorListView.as_view(), name='investor-list'),
    path('update/<int:pk>/', InvestorUpdateView.as_view(), name='investor-update'),
    path('detail/<int:pk>/', InvestorDetailView.as_view(), name='investor-detail'),
    path('export/', InvestorExportView.as_view(), name='investor-export'),
]