from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LogoutView as AuthLogoutView
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from .models import Student, Course, Enrollment, Grade
from .forms import StudentForm, CourseForm, EnrollmentForm, GradeForm, SearchForm, LoginForm

class LogoutView(AuthLogoutView):
    """Custom logout view"""
    next_page = 'login'
    
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)

def custom_login(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    
    return render(request, 'students/login.html', {'form': form})

@login_required
def dashboard(request):
    """Dashboard view with statistics"""
    total_students = Student.objects.count()
    active_students = Student.objects.filter(status='A').count()
    total_courses = Course.objects.filter(is_active=True).count()
    total_enrollments = Enrollment.objects.filter(is_active=True).count()
    
    # Recent enrollments
    recent_enrollments = Enrollment.objects.select_related('student', 'course').order_by('-enrollment_date')[:5]
    
    # Gender distribution
    gender_distribution = Student.objects.values('gender').annotate(count=Count('gender'))
    
    # Course popularity
    course_popularity = Course.objects.annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count')[:5]
    
    context = {
        'total_students': total_students,
        'active_students': active_students,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'recent_enrollments': recent_enrollments,
        'gender_distribution': gender_distribution,
        'course_popularity': course_popularity,
    }
    return render(request, 'students/dashboard.html', context)

@login_required
def student_list(request):
    """List all students with search and filter"""
    students = Student.objects.all().order_by('-created_at')
    search_form = SearchForm(request.GET)
    
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        status = search_form.cleaned_data.get('status')
        
        if query:
            students = students.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(student_id__icontains=query) |
                Q(email__icontains=query)
            )
        
        if status:
            students = students.filter(status=status)
    
    # Pagination
    paginator = Paginator(students, 10)  # Show 10 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_students': students.count(),
    }
    return render(request, 'students/student_list.html', context)

@login_required
def student_detail(request, pk):
    """View student details"""
    student = get_object_or_404(Student, pk=pk)
    enrollments = student.enrollments.select_related('course').all()
    context = {
        'student': student,
        'enrollments': enrollments,
    }
    return render(request, 'students/student_detail.html', context)

@login_required
def student_create(request):
    """Create a new student"""
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student {student.full_name()} created successfully!')
            return redirect('student_list')
    else:
        form = StudentForm()
    
    context = {'form': form}
    return render(request, 'students/student_form.html', context)

@login_required
def student_update(request, pk):
    """Update student information"""
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student {student.full_name()} updated successfully!')
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    
    context = {
        'form': form,
        'student': student,
    }
    return render(request, 'students/student_form.html', context)

@login_required
def student_delete(request, pk):
    """Delete a student"""
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        student.delete()
        messages.success(request, f'Student {student.full_name()} deleted successfully!')
        return redirect('student_list')
    
    context = {'student': student}
    return render(request, 'students/student_confirm_delete.html', context)

@login_required
def course_list(request):
    """List all courses"""
    courses = Course.objects.all().order_by('-created_at')
    context = {'courses': courses}
    return render(request, 'students/course_list.html', context)

@login_required
def course_create(request):
    """Create a new course"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course {course.course_name} created successfully!')
            return redirect('course_list')
    else:
        form = CourseForm()
    
    context = {'form': form}
    return render(request, 'students/course_form.html', context)

@login_required
def enrollment_list(request):
    """List all enrollments"""
    enrollments = Enrollment.objects.select_related('student', 'course').all().order_by('-enrollment_date')
    context = {'enrollments': enrollments}
    return render(request, 'students/enrollment_list.html', context)

@login_required
def enrollment_create(request):
    """Create a new enrollment"""
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            messages.success(request, f'Enrollment created successfully!')
            return redirect('enrollment_list')
    else:
        form = EnrollmentForm()
    
    context = {'form': form}
    return render(request, 'students/enrollment_form.html', context)

@login_required
def grade_list(request):
    """List all grades"""
    grades = Grade.objects.select_related('enrollment__student', 'enrollment__course').all().order_by('-exam_date')
    context = {'grades': grades}
    return render(request, 'students/grade_list.html', context)

@login_required
def grade_create(request):
    """Add grades for an enrollment"""
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save()
            messages.success(request, f'Grade added successfully!')
            return redirect('grade_list')
    else:
        form = GradeForm()
    
    context = {'form': form}
    return render(request, 'students/grade_form.html', context)