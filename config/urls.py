"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from apps.students import views as student_views
from apps.core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', student_views.public_home, name='home'),
    path('students/', include('apps.students.urls', namespace='students')),
    # path('students/dashboard/', student_views.StudentDashboardView.as_view(), name='student-dashboard'),

    # Auth URLs
    path('accounts/', include('apps.auth.urls')),
    path('academics/', include('apps.academics.urls')),
    path('clients/', include('apps.tenants.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('communications/', include('apps.communications.urls')),
    path('admission/', include('apps.admission.urls', namespace='admission')),
    path('exams/', include('apps.exams.urls', namespace='exams')),
    path('events/', include('apps.events.urls', namespace='events')),
    path('library/', include('apps.library.urls', namespace='library')),
    path('finance/', include('apps.finance.urls', namespace='finance')),
    path('hostel/', include('apps.hostel.urls', namespace='hostel')),
    path('hr/', include('apps.hr.urls', namespace='hr')),
    path('inventory/', include('apps.inventory.urls', namespace='inventory')),
    path('security/', include('apps.security.urls', namespace='security')),
    path('students/', include('apps.students.urls', namespace='students')),
    path('tenants/', include('apps.tenants.urls', namespace='tenants')),
    path('transportation/', include('apps.transportation.urls', namespace='transportation')),
    path('users/', include('apps.users.urls', namespace='users')),


    path('configuration/', include('apps.configuration.urls', namespace='configuration')),
    
    # Master Dashboard
    path('dashboard/', core_views.MasterDashboardView.as_view(), name='master_dashboard'),
    
    path('', include('apps.public.urls')),
    # path('accounts/login/', core_views.auth_signin, name='login'),
]
