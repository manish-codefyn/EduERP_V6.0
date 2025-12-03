
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()  # This is IMPORTANT


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form with email as username"""
    username = forms.EmailField(
        label=_("Email Address"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
        })
    )
    
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )
    
    def clean(self):
        """Add custom validation"""
        cleaned_data = super().clean()
        
        # Check if user is active
        username = cleaned_data.get('username')
        if username:
            try:
                user = User.objects.get(email=username)
                if not user.is_active:
                    raise ValidationError(
                        _("This account is inactive. Please contact administrator."),
                        code='inactive_account',
                    )
                
                if hasattr(user, 'is_account_locked') and user.is_account_locked:
                    raise ValidationError(
                        _("Your account is locked due to too many failed login attempts. "
                          "Please contact administrator or try again later."),
                        code='locked_account',
                    )
                
            except User.DoesNotExist:
                pass  # Let parent form handle this
        
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = User  # This uses the custom User model
        fields = [
            'first_name', 'last_name', 'phone_number',
            'avatar', 'timezone', 'language',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890',
            }),
            'timezone': forms.Select(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_phone_number(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Basic validation - you can add more sophisticated validation
            import re
            if not re.match(r'^\+?1?\d{9,15}$', phone):
                raise ValidationError(
                    _("Enter a valid phone number in the format: '+1234567890'")
                )
        return phone