from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    path('dashboard/', views.HRDashboardView.as_view(), name='dashboard'),
    
    # Departments
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/update/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
    
    # Designations
    path('designations/', views.DesignationListView.as_view(), name='designation_list'),
    path('designations/create/', views.DesignationCreateView.as_view(), name='designation_create'),
    path('designations/<int:pk>/update/', views.DesignationUpdateView.as_view(), name='designation_update'),
    path('designations/<int:pk>/delete/', views.DesignationDeleteView.as_view(), name='designation_delete'),
    
    # Staff
    path('staff/', views.StaffListView.as_view(), name='staff_list'),
    path('staff/<int:pk>/', views.StaffDetailView.as_view(), name='staff_detail'),
    path('staff/create/', views.StaffCreateView.as_view(), name='staff_create'),
    path('staff/<int:pk>/update/', views.StaffUpdateView.as_view(), name='staff_update'),
    path('staff/<int:pk>/delete/', views.StaffDeleteView.as_view(), name='staff_delete'),
]
