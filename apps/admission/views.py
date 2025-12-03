from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, FormView, DetailView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import AdmissionCycle, AdmissionProgram, OnlineApplication
from .forms import AdmissionApplicationForm, AdmissionStatusCheckForm

class AdmissionLandingView(TemplateView):
    template_name = 'admission/public/landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context['open_cycles'] = AdmissionCycle.objects.filter(
            status='ACTIVE',
            start_date__lte=now,
            end_date__gte=now,
            is_active=True
        )
        return context

class AdmissionApplyView(CreateView):
    model = OnlineApplication
    form_class = AdmissionApplicationForm
    template_name = 'admission/public/apply.html'
    
    def get_success_url(self):
        return reverse('admission:success', kwargs={'application_number': self.object.application_number})

    def form_valid(self, form):
        # Set default tenant if not present (assuming single tenant or handled by middleware)
        # In a multi-tenant setup, we might need to get tenant from request domain/subdomain
        # For now, we'll assume the model's save method or middleware handles it, 
        # or we might need to set it here if not.
        # Since I don't see tenant middleware in the context, I'll check if I need to set it.
        # The model has a tenant field (implied by BaseModel/TenantModel).
        # I'll assume the request has tenant attached by middleware.
        if hasattr(self.request, 'tenant'):
            form.instance.tenant = self.request.tenant
            
        response = super().form_valid(form)
        form.instance.submit_application() # Set status to SUBMITTED
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # If cycle_id or program_id is passed in URL, pre-select them
        cycle_id = self.request.GET.get('cycle')
        program_id = self.request.GET.get('program')
        
        if cycle_id:
            context['form'].fields['admission_cycle'].initial = cycle_id
        if program_id:
            context['form'].fields['program'].initial = program_id
            
        return context

class AdmissionSuccessView(TemplateView):
    template_name = 'admission/public/success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = get_object_or_404(
            OnlineApplication, 
            application_number=self.kwargs.get('application_number')
        )
        return context

class AdmissionStatusView(FormView):
    template_name = 'admission/public/status.html'
    form_class = AdmissionStatusCheckForm
    
    def form_valid(self, form):
        app_num = form.cleaned_data['application_number']
        dob = form.cleaned_data['date_of_birth']
        
        try:
            application = OnlineApplication.objects.get(
                application_number=app_num,
                date_of_birth=dob
            )
            return render(self.request, self.template_name, {
                'form': form,
                'application': application,
                'status_checked': True
            })
        except OnlineApplication.DoesNotExist:
            messages.error(self.request, _("Application not found or details incorrect."))
            return self.render_to_response(self.get_context_data(form=form))

# ==================== STAFF VIEWS ====================

class AdmissionListView(LoginRequiredMixin, ListView):
    model = OnlineApplication
    template_name = 'admission/staff/list.html'
    context_object_name = 'applications'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by tenant if applicable
        if hasattr(self.request, 'tenant'):
            queryset = queryset.filter(tenant=self.request.tenant)
            
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Search by name or application number
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(application_number__icontains=search)
            )
        return queryset

class AdmissionDetailView(LoginRequiredMixin, DetailView):
    model = OnlineApplication
    template_name = 'admission/staff/detail.html'
    context_object_name = 'application'

class AdmissionUpdateView(LoginRequiredMixin, UpdateView):
    model = OnlineApplication
    fields = ['status', 'review_date', 'decision_date', 'comments']
    template_name = 'admission/staff/form.html'
    success_url = reverse_lazy('admission:staff_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Application updated successfully."))
        return response

class AdmissionDeleteView(LoginRequiredMixin, DeleteView):
    model = OnlineApplication
    template_name = 'admission/staff/confirm_delete.html'
    success_url = reverse_lazy('admission:staff_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Application deleted successfully."))
        return super().delete(request, *args, **kwargs)

# ==================== ADMISSION CYCLE MANAGEMENT ====================

class AdmissionCycleListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = AdmissionCycle
    template_name = 'admission/staff/cycle_list.html'
    context_object_name = 'cycles'
    permission_required = 'admission.view_admissioncycle'

class AdmissionCycleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = AdmissionCycle
    fields = ['name', 'academic_year', 'code', 'school_level', 'start_date', 'end_date', 'merit_list_date', 'admission_end_date', 'status', 'max_applications', 'application_fee', 'is_active', 'instructions', 'terms_conditions']
    template_name = 'admission/staff/cycle_form.html'
    success_url = reverse_lazy('admission:cycle_list')
    permission_required = 'admission.add_admissioncycle'

    def form_valid(self, form):
        messages.success(self.request, "Admission Cycle created successfully.")
        return super().form_valid(form)

class AdmissionCycleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = AdmissionCycle
    fields = ['name', 'academic_year', 'code', 'school_level', 'start_date', 'end_date', 'merit_list_date', 'admission_end_date', 'status', 'max_applications', 'application_fee', 'is_active', 'instructions', 'terms_conditions']
    template_name = 'admission/staff/cycle_form.html'
    success_url = reverse_lazy('admission:cycle_list')
    permission_required = 'admission.change_admissioncycle'

    def form_valid(self, form):
        messages.success(self.request, "Admission Cycle updated successfully.")
        return super().form_valid(form)

class AdmissionCycleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = AdmissionCycle
    template_name = 'admission/staff/confirm_delete.html'
    success_url = reverse_lazy('admission:cycle_list')
    permission_required = 'admission.delete_admissioncycle'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Admission Cycle deleted successfully.")
        return super().delete(request, *args, **kwargs)

# ==================== ADMISSION PROGRAM MANAGEMENT ====================

class AdmissionProgramListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = AdmissionProgram
    template_name = 'admission/staff/program_list.html'
    context_object_name = 'programs'
    permission_required = 'admission.view_admissionprogram'

class AdmissionProgramCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = AdmissionProgram
    fields = ['admission_cycle', 'program_name', 'program_type', 'class_grade', 'stream', 'total_seats', 'general_seats', 'reserved_seats', 'min_age_years', 'min_age_months', 'max_age_years', 'max_age_months', 'min_qualification', 'min_percentage', 'entrance_exam_required', 'interview_required', 'eligibility_criteria', 'application_fee', 'tuition_fee', 'is_active']
    template_name = 'admission/staff/program_form.html'
    success_url = reverse_lazy('admission:program_list')
    permission_required = 'admission.add_admissionprogram'

    def form_valid(self, form):
        messages.success(self.request, "Admission Program created successfully.")
        return super().form_valid(form)

class AdmissionProgramUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = AdmissionProgram
    fields = ['admission_cycle', 'program_name', 'program_type', 'class_grade', 'stream', 'total_seats', 'general_seats', 'reserved_seats', 'min_age_years', 'min_age_months', 'max_age_years', 'max_age_months', 'min_qualification', 'min_percentage', 'entrance_exam_required', 'interview_required', 'eligibility_criteria', 'application_fee', 'tuition_fee', 'is_active']
    template_name = 'admission/staff/program_form.html'
    success_url = reverse_lazy('admission:program_list')
    permission_required = 'admission.change_admissionprogram'

    def form_valid(self, form):
        messages.success(self.request, "Admission Program updated successfully.")
        return super().form_valid(form)

class AdmissionProgramDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = AdmissionProgram
    template_name = 'admission/staff/confirm_delete.html'
    success_url = reverse_lazy('admission:program_list')
    permission_required = 'admission.delete_admissionprogram'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Admission Program deleted successfully.")
        return super().delete(request, *args, **kwargs)
