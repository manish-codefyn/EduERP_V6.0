from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.contrib.auth.mixins import AccessMixin
from django.utils.decorators import method_decorator
from django.views import View
from functools import wraps

class PermissionRequiredMixin(AccessMixin):
    """
    Mixin to require specific permissions for view access
    """
    permission_required = None
    permission_required_any = None
    raise_exception = True
    
    def get_permission_required(self):
        """
        Override this method to customize permission checking
        """
        return self.permission_required
    
    def has_permission(self):
        """
        Check if user has required permission
        """
        user = self.request.user
        
        if not user.is_authenticated:
            return False
            
        if user.is_superuser:
            return True
        
        # Check single permission
        if self.permission_required:
            if isinstance(self.permission_required, str):
                return user.has_perm(self.permission_required)
            elif isinstance(self.permission_required, (list, tuple)):
                return all(user.has_perm(perm) for perm in self.permission_required)
        
        # Check any of multiple permissions
        if self.permission_required_any:
            return any(user.has_perm(perm) for perm in self.permission_required_any)
        
        return True
    
    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            if self.raise_exception:
                raise PermissionDenied
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class RoleRequiredMixin(AccessMixin):
    """
    Mixin to require specific role(s) for view access
    """
    roles_required = None
    roles_required_any = None
    min_role_level = None
    
    def get_roles_required(self):
        return self.roles_required
    
    def has_role_permission(self):
        user = self.request.user
        
        if not user.is_authenticated:
            return False
            
        if user.is_superuser:
            return True
        
        # Check specific role(s)
        if self.roles_required:
            if isinstance(self.roles_required, str):
                return user.role == self.roles_required
            elif isinstance(self.roles_required, (list, tuple)):
                return user.role in self.roles_required
        
        # Check any of multiple roles
        if self.roles_required_any:
            return user.role in self.roles_required_any
        
        # Check minimum role level
        if self.min_role_level:
            from apps.users.models import ROLE_HIERARCHY
            user_level = ROLE_HIERARCHY.get(user.role, 0)
            return user_level >= self.min_role_level
        
        return True
    
    def dispatch(self, request, *args, **kwargs):
        if not self.has_role_permission():
            if self.raise_exception:
                raise PermissionDenied
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class TenantAccessMixin(AccessMixin):
    """
    Mixin to ensure user can only access their tenant's data
    """
    tenant_field = 'tenant'
    allow_superuser = True
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_superuser and self.allow_superuser:
            return queryset
        
        # Filter by user's tenant
        return queryset.filter(**{self.tenant_field: user.tenant})
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        
        if user.is_superuser and self.allow_superuser:
            return obj
        
        # Check if object belongs to user's tenant
        if getattr(obj, self.tenant_field) != user.tenant:
            raise Http404("Object not found or you don't have permission to view it")
        
        return obj


class ObjectPermissionMixin(AccessMixin):
    """
    Mixin for object-level permissions
    """
    object_permission_required = None
    
    def has_object_permission(self, obj):
        user = self.request.user
        
        if user.is_superuser:
            return True
        
        if self.object_permission_required:
            return user.has_perm(self.object_permission_required, obj)
        
        # Default: check if user owns the object
        return getattr(obj, 'user', None) == user or getattr(obj, 'created_by', None) == user
    
    def dispatch(self, request, *args, **kwargs):
        # For detail views, check object permissions
        if hasattr(self, 'get_object'):
            obj = self.get_object()
            if not self.has_object_permission(obj):
                raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)


class RoleBasedViewMixin(PermissionRequiredMixin, RoleRequiredMixin):
    """
    Combined mixin for both role and permission checking
    """
    def has_permission(self):
        # Check role first
        if not self.has_role_permission():
            return False
        
        # Then check specific permissions
        return super().has_permission()