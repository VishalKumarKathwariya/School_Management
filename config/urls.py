"""
URL configuration for student_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/

URL patterns tell Django which view to call for each URL.
Patterns are checked in order - first match wins.

URL Anatomy:
path('students/', views.student_list, name='student_list')
- 'students/' → URL pattern to match
- views.student_list → View function to call when pattern matches
- name='student_list' → Name for URL reversing (use in templates: {% url 'student_list' %})
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from decouple import config
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from students.views import custom_login

# Import the admin site instance for customization
admin.site.site_header = "Student Management System Admin"
admin.site.site_title = "SMS Admin Portal"
admin.site.index_title = "Welcome to Student Management System"

urlpatterns = [
    # Admin URLs
    # path('admin/', ...) would be standard, but we use configurable admin URL
    path(config('ADMIN_URL', default='admin/'), admin.site.urls),
    
    # Include app URLs
    # When Django receives a request starting with '', it will look in students.urls
    path('', include('students.urls')),
    
    # Authentication URLs
    # Using Django's built-in auth views with custom templates
    path('login/', custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Password reset URLs (optional - enable if needed)
    # path('password-reset/', 
    #      auth_views.PasswordResetView.as_view(template_name='students/password_reset.html'), 
    #      name='password_reset'),
    # path('password-reset/done/', 
    #      auth_views.PasswordResetDoneView.as_view(template_name='students/password_reset_done.html'), 
    #      name='password_reset_done'),
    # path('password-reset-confirm/<uidb64>/<token>/', 
    #      auth_views.PasswordResetConfirmView.as_view(template_name='students/password_reset_confirm.html'), 
    #      name='password_reset_confirm'),
    # path('password-reset-complete/', 
    #      auth_views.PasswordResetCompleteView.as_view(template_name='students/password_reset_complete.html'), 
    #      name='password_reset_complete'),
]

# Serve media files during development only
# In production, media files should be served by the web server (nginx, Apache)
if settings.DEBUG:
    # static() helper function creates URL patterns for serving static files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Also serve static files in development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)