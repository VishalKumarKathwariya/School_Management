from django.contrib import admin
from .models import Student, Course, Enrollment, Grade

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'email', 'status', 'enrollment_date')
    list_filter = ('status', 'gender', 'enrollment_date')
    search_fields = ('student_id', 'first_name', 'last_name', 'email')
    ordering = ('-enrollment_date',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Personal Information', {
            'fields': ('student_id', 'first_name', 'last_name', 'date_of_birth', 'gender', 'profile_picture')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Academic Information', {
            'fields': ('enrollment_date', 'status')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 20

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'course_name', 'credits', 'level', 'fee', 'is_active')
    list_filter = ('is_active', 'level')
    search_fields = ('course_code', 'course_name')
    ordering = ('course_code',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'semester', 'academic_year', 'enrollment_date', 'is_active')
    list_filter = ('is_active', 'semester', 'academic_year')
    search_fields = ('student__student_id', 'student__first_name', 'student__last_name', 'course__course_code')
    raw_id_fields = ('student', 'course')
    ordering = ('-enrollment_date',)
    list_per_page = 20

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'marks_obtained', 'total_marks', 'grade', 'exam_date')
    list_filter = ('grade', 'exam_date')
    search_fields = ('enrollment__student__student_id', 'enrollment__student__first_name')
    raw_id_fields = ('enrollment',)
    ordering = ('-exam_date',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20

# Optional: Customize admin site
admin.site.site_header = 'Student Management System Admin'
admin.site.site_title = 'Student Management System'
admin.site.index_title = 'Welcome to Student Management System Admin'