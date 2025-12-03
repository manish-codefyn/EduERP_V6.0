import threading
from contextlib import contextmanager
from django.db import connection


# Thread-local storage for tenant context
_thread_locals = threading.local()


def set_current_tenant(tenant):
    """
    Set the current tenant in thread-local storage
    """
    _thread_locals.tenant = tenant


def get_current_tenant():
    """
    Get the current tenant from thread-local storage
    """
    return getattr(_thread_locals, 'tenant', None)


def clear_tenant():
    """
    Clear tenant from thread-local storage
    """
    if hasattr(_thread_locals, 'tenant'):
        delattr(_thread_locals, 'tenant')


@contextmanager
def tenant_context(tenant):
    """
    Context manager for temporary tenant switching
    """
    old_tenant = get_current_tenant()
    set_current_tenant(tenant)
    try:
        yield
    finally:
        set_current_tenant(old_tenant)


def get_tenant_schema(tenant):
    """
    Get schema name for tenant
    """
    if hasattr(tenant, 'schema_name'):
        return tenant.schema_name
    return 'public'