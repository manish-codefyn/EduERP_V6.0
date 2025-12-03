
from django.urls import path
from . import views

app_name = 'admission'

urlpatterns = [
    # Public URLs
    path('', views.AdmissionLandingView.as_view(), name='landing'),
    path('apply/', views.AdmissionApplyView.as_view(), name='apply'),
    path('status/', views.AdmissionStatusView.as_view(), name='status'),
    path('success/<str:application_number>/', views.AdmissionSuccessView.as_view(), name='success'),
    
    # Staff URLs
    path('manage/', views.AdmissionListView.as_view(), name='staff_list'),
    path('manage/<int:pk>/', views.AdmissionDetailView.as_view(), name='staff_detail'),
    path('manage/<int:pk>/update/', views.AdmissionUpdateView.as_view(), name='staff_update'),
    path('manage/<int:pk>/delete/', views.AdmissionDeleteView.as_view(), name='staff_delete'),

    # Admission Cycle URLs
    path('cycles/', views.AdmissionCycleListView.as_view(), name='cycle_list'),
    path('cycles/create/', views.AdmissionCycleCreateView.as_view(), name='cycle_create'),
    path('cycles/<int:pk>/update/', views.AdmissionCycleUpdateView.as_view(), name='cycle_update'),
    path('cycles/<int:pk>/delete/', views.AdmissionCycleDeleteView.as_view(), name='cycle_delete'),

    # Admission Program URLs
    path('programs/', views.AdmissionProgramListView.as_view(), name='program_list'),
    path('programs/create/', views.AdmissionProgramCreateView.as_view(), name='program_create'),
    path('programs/<int:pk>/update/', views.AdmissionProgramUpdateView.as_view(), name='program_update'),
    path('programs/<int:pk>/delete/', views.AdmissionProgramDeleteView.as_view(), name='program_delete'),
]