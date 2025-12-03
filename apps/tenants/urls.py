
from django.urls import path
from . import views

app_name = "tenants"

urlpatterns = [
    path('dashboard/', views.TenantDashboardView.as_view(), name='dashboard'),
    
    # Tenants
    path('', views.TenantListView.as_view(), name='tenant_list'),
    path('<int:pk>/', views.TenantDetailView.as_view(), name='tenant_detail'),
    path('create/', views.TenantCreateView.as_view(), name='tenant_create'),
    path('<int:pk>/update/', views.TenantUpdateView.as_view(), name='tenant_update'),
    path('<int:pk>/delete/', views.TenantDeleteView.as_view(), name='tenant_delete'),
    
    # Domains
    path('domains/', views.DomainListView.as_view(), name='domain_list'),
    path('domains/create/', views.DomainCreateView.as_view(), name='domain_create'),
    path('domains/<int:pk>/update/', views.DomainUpdateView.as_view(), name='domain_update'),
    path('domains/<int:pk>/delete/', views.DomainDeleteView.as_view(), name='domain_delete'),
]
