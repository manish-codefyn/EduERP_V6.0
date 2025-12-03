from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count
from apps.core.permissions.mixins import PermissionRequiredMixin
from apps.core.utils.tenant import get_current_tenant
from .models import Department, Designation, Staff

class HRDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'hr/dashboard.html'
    permission_required = 'hr.view_staff'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = get_current_tenant()
        
        context['total_staff'] = Staff.objects.filter(tenant=tenant, is_active=True).count()
        context['total_departments'] = Department.objects.filter(tenant=tenant).count()
        context['total_designations'] = Designation.objects.filter(tenant=tenant).count()
        context['active_staff'] = Staff.objects.filter(tenant=tenant, employment_status='ACTIVE').count()
        
        return context

# ==================== DEPARTMENT ====================

class DepartmentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Department
    template_name = 'hr/department_list.html'
    context_object_name = 'departments'
    permission_required = 'hr.view_department'

class DepartmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Department
    fields = ['name', 'code', 'description', 'head_of_department', 'email', 'phone', 'location']
    template_name = 'hr/department_form.html'
    success_url = reverse_lazy('hr:department_list')
    permission_required = 'hr.add_department'

    def form_valid(self, form):
        messages.success(self.request, "Department created successfully.")
        return super().form_valid(form)

class DepartmentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Department
    fields = ['name', 'code', 'description', 'head_of_department', 'email', 'phone', 'location']
    template_name = 'hr/department_form.html'
    success_url = reverse_lazy('hr:department_list')
    permission_required = 'hr.change_department'

    def form_valid(self, form):
        messages.success(self.request, "Department updated successfully.")
        return super().form_valid(form)

class DepartmentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Department
    template_name = 'hr/confirm_delete.html'
    success_url = reverse_lazy('hr:department_list')
    permission_required = 'hr.delete_department'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Department deleted successfully.")
        return super().delete(request, *args, **kwargs)

# ==================== DESIGNATION ====================

class DesignationListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Designation
    template_name = 'hr/designation_list.html'
    context_object_name = 'designations'
    permission_required = 'hr.view_designation'

class DesignationCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Designation
    fields = ['title', 'code', 'category', 'description', 'grade', 'min_salary', 
              'max_salary', 'qualifications', 'experience_required', 'reports_to']
    template_name = 'hr/designation_form.html'
    success_url = reverse_lazy('hr:designation_list')
    permission_required = 'hr.add_designation'

    def form_valid(self, form):
        messages.success(self.request, "Designation created successfully.")
        return super().form_valid(form)

class DesignationUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Designation
    fields = ['title', 'code', 'category', 'description', 'grade', 'min_salary', 
              'max_salary', 'qualifications', 'experience_required', 'reports_to']
    template_name = 'hr/designation_form.html'
    success_url = reverse_lazy('hr:designation_list')
    permission_required = 'hr.change_designation'

    def form_valid(self, form):
        messages.success(self.request, "Designation updated successfully.")
        return super().form_valid(form)

class DesignationDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Designation
    template_name = 'hr/confirm_delete.html'
    success_url = reverse_lazy('hr:designation_list')
    permission_required = 'hr.delete_designation'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Designation deleted successfully.")
        return super().delete(request, *args, **kwargs)

# ==================== STAFF ====================

class StaffListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Staff
    template_name = 'hr/staff_list.html'
    context_object_name = 'staff_members'
    permission_required = 'hr.view_staff'

class StaffDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Staff
    template_name = 'hr/staff_detail.html'
    context_object_name = 'staff'
    permission_required = 'hr.view_staff'

class StaffCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Staff
    fields = ['user', 'employee_id', 'date_of_birth', 'gender', 'blood_group', 
              'marital_status', 'nationality', 'employment_type', 'employment_status', 
              'joining_date', 'is_active']
    template_name = 'hr/staff_form.html'
    success_url = reverse_lazy('hr:staff_list')
    permission_required = 'hr.add_staff'

    def form_valid(self, form):
        messages.success(self.request, "Staff member created successfully.")
        return super().form_valid(form)

class StaffUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Staff
    fields = ['user', 'employee_id', 'date_of_birth', 'gender', 'blood_group', 
              'marital_status', 'nationality', 'employment_type', 'employment_status', 
              'joining_date', 'is_active']
    template_name = 'hr/staff_form.html'
    success_url = reverse_lazy('hr:staff_list')
    permission_required = 'hr.change_staff'

    def form_valid(self, form):
        messages.success(self.request, "Staff member updated successfully.")
        return super().form_valid(form)

class StaffDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Staff
    template_name = 'hr/confirm_delete.html'
    success_url = reverse_lazy('hr:staff_list')
    permission_required = 'hr.delete_staff'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Staff member deleted successfully.")
        return super().delete(request, *args, **kwargs)
