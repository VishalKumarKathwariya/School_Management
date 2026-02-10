from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('A', 'Active'),
        ('I', 'Inactive'),
        ('G', 'Graduated'),
        ('T', 'Transferred'),
    ]
    
    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    profile_picture = models.ImageField(upload_to='student_profiles/', null=True, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-enrollment_date', 'last_name']
    
    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

class Course(models.Model):
    LEVEL_CHOICES = [
        ('UG', 'Undergraduate'),
        ('PG', 'Postgraduate'),
        ('DP', 'Diploma'),
        ('CR', 'Certificate'),
    ]
    
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=200)
    description = models.TextField()
    credits = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)])
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES)
    duration_months = models.IntegerField()
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.course_code} - {self.course_name}"

class Enrollment(models.Model):
    SEMESTER_CHOICES = [
        ('S1', 'Semester 1'),
        ('S2', 'Semester 2'),
        ('S3', 'Semester 3'),
        ('S4', 'Semester 4'),
        ('S5', 'Semester 5'),
        ('S6', 'Semester 6'),
        ('S7', 'Semester 7'),
        ('S8', 'Semester 8'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES)
    academic_year = models.CharField(max_length=9)  # Format: 2023-2024
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['student', 'course', 'semester', 'academic_year']
        ordering = ['-enrollment_date']
    
    def __str__(self):
        return f"{self.student} - {self.course} ({self.semester} {self.academic_year})"

class Grade(models.Model):
    GRADE_CHOICES = [
        ('A', 'A (90-100)'),
        ('B', 'B (80-89)'),
        ('C', 'C (70-79)'),
        ('D', 'D (60-69)'),
        ('E', 'E (50-59)'),
        ('F', 'F (Below 50)'),
    ]
    
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='grades')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES)
    remarks = models.TextField(blank=True)
    exam_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"{self.enrollment} - {self.grade}"
    
    def percentage(self):
        return (self.marks_obtained / self.total_marks) * 100