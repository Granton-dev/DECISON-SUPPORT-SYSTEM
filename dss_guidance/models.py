from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class AcademicProgram(models.Model):
    FACULTY_CHOICES = [
        ('business', 'Business'),
        ('agriculture', 'Agriculture'),
        ('computing', 'Computing & IT'),
        ('education', 'Education'),
        ('science', 'Science'),
        ('engineering', 'Engineering'),
    ]

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    faculty = models.CharField(max_length=50, choices=FACULTY_CHOICES)
    description = models.TextField()
    duration_years = models.PositiveIntegerField(default=4)
    minimum_grade = models.CharField(max_length=5, help_text="Minimum KCSE grade e.g. C+")
    minimum_points = models.PositiveIntegerField(help_text="Minimum KCSE points (out of 84)")
    required_subjects = models.TextField(help_text="Comma-separated list of required subjects")
    skills_developed = models.TextField(help_text="Comma-separated list of skills")
    career_paths = models.TextField(help_text="Comma-separated possible careers")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_required_subjects_list(self):
        return [s.strip() for s in self.required_subjects.split(',') if s.strip()]

    def get_skills_list(self):
        return [s.strip() for s in self.skills_developed.split(',') if s.strip()]

    def get_career_paths_list(self):
        return [c.strip() for c in self.career_paths.split(',') if c.strip()]

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['faculty', 'name']


class StudentProfile(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    county = models.CharField(max_length=100, blank=True)
    current_program = models.ForeignKey(
        AcademicProgram, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='enrolled_students'
    )
    year_of_study = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    enrollment_year = models.PositiveIntegerField(null=True, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"

    class Meta:
        ordering = ['student_id']


class KCSEResult(models.Model):
    GRADE_CHOICES = [
        ('A', 'A (81–84)'), ('A-', 'A- (74–80)'),
        ('B+', 'B+ (67–73)'), ('B', 'B (60–66)'),
        ('B-', 'B- (53–59)'), ('C+', 'C+ (46–52)'),
        ('C', 'C (40–45)'), ('C-', 'C- (33–39)'),
        ('D+', 'D+ (26–32)'), ('D', 'D (20–25)'),
        ('D-', 'D- (13–19)'), ('E', 'E (00–12)'),
    ]

    student = models.OneToOneField(
        StudentProfile, on_delete=models.CASCADE, related_name='kcse_result'
    )
    index_number = models.CharField(max_length=20, unique=True)
    year = models.PositiveIntegerField()
    overall_grade = models.CharField(max_length=3, choices=GRADE_CHOICES)
    total_points = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(84)]
    )
    # Core subjects
    mathematics = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    english = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    kiswahili = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    biology = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    chemistry = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    physics = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    history = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    geography = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    business_studies = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    agriculture = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    computer_studies = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_subject_grades(self):
        subjects = {
            'Mathematics': self.mathematics,
            'English': self.english,
            'Kiswahili': self.kiswahili,
            'Biology': self.biology,
            'Chemistry': self.chemistry,
            'Physics': self.physics,
            'History': self.history,
            'Geography': self.geography,
            'Business Studies': self.business_studies,
            'Agriculture': self.agriculture,
            'Computer Studies': self.computer_studies,
        }
        return {k: v for k, v in subjects.items() if v}

    def __str__(self):
        return f"{self.student} - {self.overall_grade} ({self.total_points} pts)"


class UniversityPerformance(models.Model):
    GRADE_CHOICES = [
        ('A', 'A (70–100%)'), ('B+', 'B+ (65–69%)'),
        ('B', 'B (60–64%)'), ('C+', 'C+ (55–59%)'),
        ('C', 'C (50–54%)'), ('D+', 'D+ (45–49%)'),
        ('D', 'D (40–44%)'), ('E', 'E (Below 40%)'),
    ]

    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name='university_performance'
    )
    unit_code = models.CharField(max_length=20)
    unit_name = models.CharField(max_length=200)
    year = models.PositiveIntegerField()
    semester = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)])
    grade = models.CharField(max_length=3, choices=GRADE_CHOICES)
    marks = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.unit_code} - {self.grade}"

    class Meta:
        unique_together = ('student', 'unit_code', 'year', 'semester')
        ordering = ['year', 'semester']


class StudentInterest(models.Model):
    INTEREST_LEVEL = [
        (1, 'Not Interested'),
        (2, 'Slightly Interested'),
        (3, 'Moderately Interested'),
        (4, 'Interested'),
        (5, 'Very Interested'),
    ]

    student = models.OneToOneField(
        StudentProfile, on_delete=models.CASCADE, related_name='interests'
    )
    # Career interests
    technology = models.IntegerField(choices=INTEREST_LEVEL, default=3)
    business_finance = models.IntegerField(choices=INTEREST_LEVEL, default=3)
    healthcare = models.IntegerField(choices=INTEREST_LEVEL, default=3)
    education_teaching = models.IntegerField(choices=INTEREST_LEVEL, default=3)
    agriculture_environment = models.IntegerField(choices=INTEREST_LEVEL, default=3)
    engineering = models.IntegerField(choices=INTEREST_LEVEL, default=3)
    research_science = models.IntegerField(choices=INTEREST_LEVEL, default=3)
    arts_communication = models.IntegerField(choices=INTEREST_LEVEL, default=3)
    # Work style
    prefers_fieldwork = models.BooleanField(default=False)
    prefers_research = models.BooleanField(default=False)
    prefers_people_interaction = models.BooleanField(default=False)
    prefers_technical_work = models.BooleanField(default=False)
    career_goal = models.TextField(blank=True, help_text="Describe your career goal")
    preferred_work_location = models.CharField(
        max_length=20,
        choices=[('urban', 'Urban'), ('rural', 'Rural'), ('both', 'Both')],
        default='both'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Interests - {self.student}"


class Recommendation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed by Advisor'),
        ('accepted', 'Accepted by Student'),
        ('declined', 'Declined by Student'),
    ]

    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name='recommendations'
    )
    program = models.ForeignKey(
        AcademicProgram, on_delete=models.CASCADE, related_name='recommendations'
    )
    match_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    reasoning = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    advisor_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviewed_recommendations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student} → {self.program.code} ({self.match_score}%)"

    class Meta:
        ordering = ['-match_score']


class AdvisorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='advisor_profile')
    staff_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    specialization = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    office_location = models.CharField(max_length=100, blank=True)
    assigned_students = models.ManyToManyField(
        StudentProfile, blank=True, related_name='advisors'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.staff_id} - {self.user.get_full_name()}"


class AdvisorySession(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    advisor = models.ForeignKey(
        AdvisorProfile, on_delete=models.CASCADE, related_name='sessions'
    )
    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name='sessions'
    )
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    outcome = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.advisor} ↔ {self.student} on {self.scheduled_date.date()}"

    class Meta:
        ordering = ['-scheduled_date']
