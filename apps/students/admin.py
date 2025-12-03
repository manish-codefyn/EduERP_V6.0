from django.contrib import admin
from .models import (
    Student, Guardian, StudentAddress, StudentDocument,
    StudentMedicalInfo, StudentAcademicHistory, StudentIdentification
)

class GuardianInline(admin.StackedInline):
    model = Guardian
    extra = 0

class StudentAddressInline(admin.StackedInline):
    model = StudentAddress
    extra = 0

class StudentDocumentInline(admin.TabularInline):
    model = StudentDocument
    extra = 0

class StudentMedicalInfoInline(admin.StackedInline):
    model = StudentMedicalInfo
    can_delete = False
    verbose_name_plural = 'Medical Information'

class StudentIdentificationInline(admin.StackedInline):
    model = StudentIdentification
    can_delete = False
    verbose_name_plural = 'Identification'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'full_name', 'current_class', 'section', 'status', 'gender', 'enrollment_date')
    list_filter = ('status', 'gender', 'current_class', 'section', 'admission_type', 'category')
    search_fields = ('admission_number', 'first_name', 'last_name', 'personal_email', 'mobile_primary')
    inlines = [StudentAddressInline, GuardianInline, StudentDocumentInline, StudentMedicalInfoInline, StudentIdentificationInline]
    date_hierarchy = 'enrollment_date'
    fieldsets = (
        ('Core Identification', {
            'fields': ('user', 'admission_number', 'roll_number', 'university_reg_no')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'date_of_birth', 'place_of_birth', 'gender', 'blood_group', 'nationality', 'marital_status')
        }),
        ('Contact Information', {
            'fields': ('personal_email', 'institutional_email', 'mobile_primary', 'mobile_secondary')
        }),
        ('Academic Information', {
            'fields': ('admission_type', 'enrollment_date', 'academic_year', 'current_class', 'stream', 'section')
        }),
        ('Socio-Economic Information', {
            'fields': ('category', 'religion', 'is_minority', 'is_physically_challenged', 'annual_family_income')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'status_changed_date', 'graduation_date')
        }),
        ('Academic Tracking', {
            'fields': ('current_semester', 'total_credits_earned', 'cumulative_grade_point')
        }),
        ('Fee & Financial', {
            'fields': ('fee_category', 'scholarship_type')
        }),
        ('System', {
            'fields': ('created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'student', 'relation', 'is_primary', 'phone_primary', 'email')
    list_filter = ('relation', 'is_primary', 'is_emergency_contact')
    search_fields = ('full_name', 'student__first_name', 'student__last_name', 'phone_primary', 'email')

@admin.register(StudentAddress)
class StudentAddressAdmin(admin.ModelAdmin):
    list_display = ('student', 'address_type', 'city', 'state', 'pincode', 'is_current')
    list_filter = ('address_type', 'is_current', 'city')
    search_fields = ('student__first_name', 'student__last_name', 'address_line1', 'city', 'pincode')

@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ('student', 'doc_type', 'status', 'is_verified', 'expiry_date')
    list_filter = ('doc_type', 'status', 'is_verified')
    search_fields = ('student__first_name', 'student__last_name', 'file_name')

@admin.register(StudentMedicalInfo)
class StudentMedicalInfoAdmin(admin.ModelAdmin):
    list_display = ('student', 'blood_group', 'has_disability', 'has_medical_insurance')
    list_filter = ('blood_group', 'has_disability', 'has_medical_insurance')
    search_fields = ('student__first_name', 'student__last_name')

@admin.register(StudentAcademicHistory)
class StudentAcademicHistoryAdmin(admin.ModelAdmin):
    list_display = ('student', 'academic_year', 'class_name', 'result', 'percentage')
    list_filter = ('academic_year', 'class_name', 'result')
    search_fields = ('student__first_name', 'student__last_name')

@admin.register(StudentIdentification)
class StudentIdentificationAdmin(admin.ModelAdmin):
    list_display = ('student', 'aadhaar_verified', 'pan_verified', 'passport_verified')
    list_filter = ('aadhaar_verified', 'pan_verified', 'passport_verified')
    search_fields = ('student__first_name', 'student__last_name')
