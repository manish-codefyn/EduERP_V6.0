# apps/users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Q
from .models import User
from apps.tenants.models import Tenant


class TenantAwareUserCreationForm(UserCreationForm):
    """Custom user creation form with tenant awareness"""
    
    # Remove password2 field from initial display, we'll handle it differently
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_("Enter a strong password with at least 8 characters."),
    )
    
    password2 = None  # We'll validate password in clean method
    
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label=_("Organization"),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_("Select the organization this user belongs to.")
    )
    
    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'tenant',
            'role',
            'phone_number',
            'date_of_birth',
            'timezone',
            'language',
            'is_active',
        )
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'user@example.com'
            }),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'timezone': forms.Select(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'email': _('Required. A valid email address.'),
            'role': _('Select the user role based on their responsibilities.'),
        }
    
    def __init__(self, *args, **kwargs):
        # Get the request user from kwargs if provided
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        
        # Set required fields based on tenant requirement
        if self.request_user and self.request_user.is_superuser:
            # Superusers can create users for any tenant or no tenant
            self.fields['tenant'].required = False
        else:
            # Regular users can only create users for their own tenant
            if self.request_user and self.request_user.tenant:
                self.fields['tenant'].queryset = Tenant.objects.filter(
                    id=self.request_user.tenant.id
                )
                self.fields['tenant'].initial = self.request_user.tenant
                self.fields['tenant'].widget.attrs['readonly'] = True
                self.fields['tenant'].required = True
            else:
                self.fields['tenant'].required = True
        
        # Hide tenant field if there's only one option
        if 'tenant' in self.fields and self.fields['tenant'].queryset.count() == 1:
            self.fields['tenant'].widget = forms.HiddenInput()
        
        # Adjust role choices based on user permissions
        if self.request_user and not self.request_user.is_superuser:
            role_choices = []
            for role_value, role_label in User.ROLE_CHOICES:
                # Prevent regular users from creating super_admin or admin roles
                if role_value not in [User.ROLE_SUPER_ADMIN, User.ROLE_ADMIN]:
                    role_choices.append((role_value, role_label))
            self.fields['role'].choices = role_choices
        
        # Add password confirmation field dynamically
        self.fields['confirm_password'] = forms.CharField(
            label=_("Confirm Password"),
            widget=forms.PasswordInput(attrs={
                'class': 'form-control',
                'autocomplete': 'new-password'
            }),
            help_text=_("Enter the same password as above, for verification.")
        )
    
    def clean_email(self):
        """Validate email uniqueness within tenant"""
        email = self.cleaned_data.get('email')
        tenant = self.cleaned_data.get('tenant')
        
        if not email:
            return email
        
        # Check if email exists within the same tenant
        users_with_email = User.objects.filter(email=email)
        
        if tenant:
            users_with_email = users_with_email.filter(tenant=tenant)
        
        if self.instance.pk:
            users_with_email = users_with_email.exclude(pk=self.instance.pk)
        
        if users_with_email.exists():
            if tenant:
                raise ValidationError(
                    _("A user with this email already exists in this organization.")
                )
            else:
                raise ValidationError(
                    _("A user with this email already exists.")
                )
        
        return email.lower()
    
    def clean(self):
        """Form-wide validation"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        confirm_password = cleaned_data.get('confirm_password')
        tenant = cleaned_data.get('tenant')
        is_superuser = self.instance.is_superuser if self.instance else False
        
        # Validate password confirmation
        if password1 and confirm_password and password1 != confirm_password:
            self.add_error('confirm_password', _("Passwords do not match."))
        
        # Validate password strength
        if password1 and len(password1) < 8:
            self.add_error('password1', _("Password must be at least 8 characters long."))
        
        # Validate tenant requirement for non-superusers
        if not tenant and not is_superuser:
            if self.request_user and self.request_user.is_superuser:
                # Superuser creating a regular user
                self.add_error('tenant', _("Tenant is required for non-superuser accounts."))
            else:
                # Regular user creating another user
                self.add_error('tenant', _("Organization is required."))
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save user with password"""
        user = super().save(commit=False)
        
        # Set password if provided
        if 'password1' in self.cleaned_data and self.cleaned_data['password1']:
            user.set_password(self.cleaned_data['password1'])
        
        # Generate verification token for new non-superusers
        if not user.pk and not user.is_superuser:
            user.generate_verification_token()
        
        if commit:
            user.save()
        
        return user


class TenantAwareUserChangeForm(UserChangeForm):
    """Custom user change form with tenant awareness"""
    
    current_password = forms.CharField(
        label=_("Current Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'current-password'
        }),
        required=False,
        help_text=_("Enter your current password to confirm changes.")
    )
    
    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'tenant',
            'role',
            'phone_number',
            'date_of_birth',
            'avatar',
            'timezone',
            'language',
            'student_id',
            'employee_id',
            'is_active',
            'is_verified',
            'mfa_enabled',
        )
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tenant': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'timezone': forms.Select(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mfa_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        
        # Make email read-only for existing users
        if self.instance.pk:
            self.fields['email'].widget.attrs['readonly'] = True
        
        # Handle tenant field based on permissions
        if 'tenant' in self.fields:
            if self.request_user:
                if self.request_user.is_superuser:
                    # Superusers can change tenant
                    self.fields['tenant'].required = not self.instance.is_superuser
                else:
                    # Regular users can't change tenant
                    self.fields['tenant'].queryset = Tenant.objects.filter(
                        id=self.request_user.tenant.id
                    )
                    self.fields['tenant'].widget.attrs['disabled'] = True
                    self.fields['tenant'].required = True
        
        # Handle role field based on permissions
        if self.request_user and not self.request_user.is_superuser:
            role_choices = []
            for role_value, role_label in User.ROLE_CHOICES:
                # Prevent regular users from assigning super_admin or admin roles
                if role_value not in [User.ROLE_SUPER_ADMIN, User.ROLE_ADMIN]:
                    role_choices.append((role_value, role_label))
            self.fields['role'].choices = role_choices
        
        # Hide sensitive fields from non-superusers
        if self.request_user and not self.request_user.is_superuser:
            if 'is_verified' in self.fields:
                self.fields['is_verified'].widget = forms.HiddenInput()
            if 'mfa_enabled' in self.fields:
                self.fields['mfa_enabled'].widget = forms.HiddenInput()
        
        # Remove password field from form
        if 'password' in self.fields:
            del self.fields['password']
    
    def clean_email(self):
        """Ensure email uniqueness within tenant"""
        email = self.cleaned_data.get('email')
        tenant = self.cleaned_data.get('tenant')
        
        if not email:
            return email
        
        # Check for duplicate email within the same tenant
        users_with_email = User.objects.filter(email=email)
        
        if tenant:
            users_with_email = users_with_email.filter(tenant=tenant)
        else:
            users_with_email = users_with_email.filter(tenant__isnull=True)
        
        if self.instance.pk:
            users_with_email = users_with_email.exclude(pk=self.instance.pk)
        
        if users_with_email.exists():
            if tenant:
                raise ValidationError(
                    _("A user with this email already exists in this organization.")
                )
            else:
                raise ValidationError(
                    _("A user with this email already exists.")
                )
        
        return email.lower()
    
    def clean(self):
        """Form-wide validation"""
        cleaned_data = super().clean()
        
        # Validate tenant requirement for non-superusers
        tenant = cleaned_data.get('tenant')
        if not tenant and not self.instance.is_superuser:
            self.add_error('tenant', _("Organization is required for non-superuser accounts."))
        
        # For superusers editing their own profile, don't require current password
        if self.request_user and self.request_user == self.instance:
            return cleaned_data
        
        # For sensitive changes, require current password
        sensitive_fields = ['role', 'is_active', 'is_verified']
        if any(field in self.changed_data for field in sensitive_fields):
            current_password = cleaned_data.get('current_password')
            if not current_password:
                self.add_error('current_password', 
                    _("Current password is required for sensitive changes.")
                )
            elif not self.request_user.check_password(current_password):
                self.add_error('current_password', 
                    _("Current password is incorrect.")
                )
        
        return cleaned_data


class TenantAwarePasswordChangeForm(PasswordChangeForm):
    """Custom password change form"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'new-password'
            })
    
    def clean_new_password2(self):
        """Validate password strength"""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Passwords do not match."))
        
        if password1 and len(password1) < 8:
            raise ValidationError(_("Password must be at least 8 characters long."))
        
        # Add more password strength checks as needed
        # if not any(char.isdigit() for char in password1):
        #     raise ValidationError(_("Password must contain at least one digit."))
        
        return password2


class UserProfileForm(forms.ModelForm):
    """Form for users to edit their own profile"""
    
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'phone_number',
            'date_of_birth',
            'avatar',
            'timezone',
            'language',
        )
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'timezone': forms.Select(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required for profile completion
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True


class BulkUserImportForm(forms.Form):
    """Form for bulk user import"""
    
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all(),
        required=True,
        label=_("Organization"),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_("Select the organization for imported users.")
    )
    
    csv_file = forms.FileField(
        label=_("CSV File"),
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        help_text=_("Upload a CSV file with columns: email,first_name,last_name,role,phone_number")
    )
    
    default_password = forms.CharField(
        label=_("Default Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text=_("Leave empty to generate random passwords.")
    )
    
    send_welcome_email = forms.BooleanField(
        label=_("Send welcome email"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text=_("Send welcome email to new users with login instructions.")
    )
    
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        
        # Limit tenant choices for non-superusers
        if self.request_user and not self.request_user.is_superuser:
            self.fields['tenant'].queryset = Tenant.objects.filter(
                id=self.request_user.tenant.id
            )
            self.fields['tenant'].initial = self.request_user.tenant
            self.fields['tenant'].widget.attrs['disabled'] = True


class UserFilterForm(forms.Form):
    """Form for filtering users"""
    
    ROLE_CHOICES = [('', 'All Roles')] + User.ROLE_CHOICES
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=False,
        label=_("Role"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    is_active = forms.ChoiceField(
        choices=[('', 'All'), ('active', 'Active'), ('inactive', 'Inactive')],
        required=False,
        label=_("Status"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    is_verified = forms.ChoiceField(
        choices=[('', 'All'), ('verified', 'Verified'), ('unverified', 'Unverified')],
        required=False,
        label=_("Verification"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    search = forms.CharField(
        required=False,
        label=_("Search"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search by name, email, or ID')
        })
    )
    
    def filter_queryset(self, queryset):
        """Apply filters to queryset"""
        data = self.cleaned_data
        
        if data.get('role'):
            queryset = queryset.filter(role=data['role'])
        
        if data.get('is_active') == 'active':
            queryset = queryset.filter(is_active=True)
        elif data.get('is_active') == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        if data.get('is_verified') == 'verified':
            queryset = queryset.filter(is_verified=True)
        elif data.get('is_verified') == 'unverified':
            queryset = queryset.filter(is_verified=False)
        
        if data.get('search'):
            search_term = data['search']
            queryset = queryset.filter(
                Q(email__icontains=search_term) |
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(student_id__icontains=search_term) |
                Q(employee_id__icontains=search_term) |
                Q(phone_number__icontains=search_term)
            )
        
        return queryset


class MFAEnableForm(forms.Form):
    """Form for enabling MFA"""
    
    verification_code = forms.CharField(
        label=_("Verification Code"),
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123456',
            'autocomplete': 'off'
        }),
        help_text=_("Enter the 6-digit code from your authenticator app.")
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_verification_code(self):
        """Verify the MFA code"""
        code = self.cleaned_data.get('verification_code')
        
        if not code or len(code) != 6:
            raise ValidationError(_("Invalid verification code format."))
        
        if self.user and not self.user.verify_mfa_token(code):
            raise ValidationError(_("Invalid verification code. Please try again."))
        
        return code


class MFADisableForm(forms.Form):
    """Form for disabling MFA"""
    
    password = forms.CharField(
        label=_("Current Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'current-password'
        }),
        help_text=_("Enter your current password to disable MFA.")
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_password(self):
        """Verify the password"""
        password = self.cleaned_data.get('password')
        
        if self.user and not self.user.check_password(password):
            raise ValidationError(_("Incorrect password."))
        
        return password