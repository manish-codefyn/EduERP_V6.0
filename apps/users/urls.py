from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('dashboard/', views.UserDashboardView.as_view(), name='dashboard'),
    
    # User CRUD
    path('', views.UserListView.as_view(), name='user_list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('create/', views.UserCreateView.as_view(), name='user_create'),
    path('<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),
    path('<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    
    # Profile Management
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Admin Actions (AJAX)
    path('<int:pk>/toggle-status/', views.ToggleUserStatusView.as_view(), name='toggle_status'),
    path('<int:pk>/toggle-verification/', views.ToggleUserVerificationView.as_view(), name='toggle_verification'),
    path('<int:pk>/toggle-staff/', views.ToggleUserStaffView.as_view(), name='toggle_staff'),
    path('<int:pk>/reset-password/', views.ResetUserPasswordView.as_view(), name='reset_password'),
]
