from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('dashboard/', views.FinanceDashboardView.as_view(), name='dashboard'),
    
    # Fee Structures
    path('fee-structures/', views.FeeStructureListView.as_view(), name='fee_structure_list'),
    path('fee-structures/create/', views.FeeStructureCreateView.as_view(), name='fee_structure_create'),
    path('fee-structures/<int:pk>/update/', views.FeeStructureUpdateView.as_view(), name='fee_structure_update'),
    path('fee-structures/<int:pk>/delete/', views.FeeStructureDeleteView.as_view(), name='fee_structure_delete'),
    
    # Fee Discounts
    path('discounts/', views.FeeDiscountListView.as_view(), name='fee_discount_list'),
    path('discounts/create/', views.FeeDiscountCreateView.as_view(), name='fee_discount_create'),
    path('discounts/<int:pk>/update/', views.FeeDiscountUpdateView.as_view(), name='fee_discount_update'),
    path('discounts/<int:pk>/delete/', views.FeeDiscountDeleteView.as_view(), name='fee_discount_delete'),
    
    # Invoices
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/create/', views.InvoiceCreateView.as_view(), name='invoice_create'),
    path('invoices/<int:pk>/update/', views.InvoiceUpdateView.as_view(), name='invoice_update'),
    path('invoices/<int:pk>/delete/', views.InvoiceDeleteView.as_view(), name='invoice_delete'),
    
    # Payments
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('payments/create/', views.PaymentCreateView.as_view(), name='payment_create'),
]
