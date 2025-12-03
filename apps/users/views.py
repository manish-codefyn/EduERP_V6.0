from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Count, Q
from apps.core.permissions.mixins import PermissionRequiredMixin
from apps.core.utils.tenant import get_current_tenant
from .models import User

class UserDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'users/dashboard.html'
    permission_required = 'users.view_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = get_current_tenant()
        
        context['total_users'] = User.objects.filter(tenant=tenant).count()
        context['active_users'] = User.objects.filter(tenant=tenant, is_active=True).count()
        context['verified_users'] = User.objects.filter(tenant=tenant, is_verified=True).count()
        context['staff_users'] = User.objects.filter(tenant=tenant, is_staff=True).count()
        
        return context

# ==================== USER CRUD ====================

class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    permission_required = 'users.view_user'

    def get_queryset(self):
        queryset = super().get_queryset()
        tenant = get_current_tenant()
        return queryset.filter(tenant=tenant)

class UserDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user_obj'
    permission_required = 'users.view_user'

class UserCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = User
    fields = ['email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 
              'role', 'avatar', 'is_active', 'is_staff', 'is_verified']
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user_list')
    permission_required = 'users.add_user'

    def form_valid(self, form):
        form.instance.tenant = get_current_tenant()
        # Set a temporary password
        form.instance.set_password('TempPassword123!')
        messages.success(self.request, "User created successfully. Temporary password: TempPassword123!")
        return super().form_valid(form)

class UserUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    fields = ['email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 
              'role', 'avatar', 'is_active', 'is_staff', 'is_verified']
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user_list')
    permission_required = 'users.change_user'

    def form_valid(self, form):
        messages.success(self.request, "User updated successfully.")
        return super().form_valid(form)

class UserDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = User
    template_name = 'users/confirm_delete.html'
    success_url = reverse_lazy('users:user_list')
    permission_required = 'users.delete_user'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "User deleted successfully.")
        return super().delete(request, *args, **kwargs)

# ==================== PROFILE MANAGEMENT ====================

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_obj'] = self.request.user
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'phone_number', 'date_of_birth', 'avatar', 'timezone', 'language']
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)

class ChangePasswordView(LoginRequiredMixin, TemplateView):
    template_name = 'users/change_password.html'

    def post(self, request, *args, **kwargs):
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not user.check_password(old_password):
            messages.error(request, "Old password is incorrect.")
            return redirect('users:change_password')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('users:change_password')

        user.set_password(new_password)
        user.save()
        messages.success(request, "Password changed successfully. Please login again.")
        return redirect('login')

# ==================== ADMIN ACTIONS ====================

class ToggleUserStatusView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Toggle user active status via AJAX"""
    permission_required = 'users.change_user'

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, tenant=get_current_tenant())
        user.is_active = not user.is_active
        user.save()
        
        return JsonResponse({
            'success': True,
            'is_active': user.is_active,
            'message': f"User {'activated' if user.is_active else 'deactivated'} successfully."
        })

class ToggleUserVerificationView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Toggle user verification status via AJAX"""
    permission_required = 'users.change_user'

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, tenant=get_current_tenant())
        user.is_verified = not user.is_verified
        user.save()
        
        return JsonResponse({
            'success': True,
            'is_verified': user.is_verified,
            'message': f"User verification {'enabled' if user.is_verified else 'disabled'} successfully."
        })

class ToggleUserStaffView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Toggle user staff status via AJAX"""
    permission_required = 'users.change_user'

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, tenant=get_current_tenant())
        user.is_staff = not user.is_staff
        user.save()
        
        return JsonResponse({
            'success': True,
            'is_staff': user.is_staff,
            'message': f"User staff status {'enabled' if user.is_staff else 'disabled'} successfully."
        })

class ResetUserPasswordView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Reset user password to default"""
    permission_required = 'users.change_user'

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, tenant=get_current_tenant())
        new_password = 'TempPassword123!'
        user.set_password(new_password)
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': f"Password reset successfully. New password: {new_password}"
        })
