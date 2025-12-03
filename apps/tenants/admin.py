from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import Tenant, Domain, TenantConfiguration

class DomainInline(admin.TabularInline):
    model = Domain
    extra = 0

class TenantConfigurationInline(admin.StackedInline):
    model = TenantConfiguration
    can_delete = False
    verbose_name_plural = 'Configuration'

@admin.register(Tenant)
class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'schema_name', 'status', 'plan', 'is_active')
    list_filter = ('status', 'plan', 'is_active')
    search_fields = ('name', 'schema_name', 'contact_email')
    inlines = [DomainInline, TenantConfigurationInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'display_name', 'schema_name', 'slug')
        }),
        ('Status & Plan', {
            'fields': ('status', 'plan', 'is_active', 'trial_ends_at', 'subscription_ends_at')
        }),
        ('Limits', {
            'fields': ('max_users', 'max_storage_mb')
        }),
        ('Contact', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Security', {
            'fields': ('force_password_reset', 'mfa_required', 'password_policy')
        }),
    )

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary', 'is_verified', 'ssl_enabled')
    list_filter = ('is_primary', 'is_verified', 'ssl_enabled')
    search_fields = ('domain', 'tenant__name')

@admin.register(TenantConfiguration)
class TenantConfigurationAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'academic_year', 'language', 'currency', 'timezone')
    search_fields = ('tenant__name',)
