from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import (
    StudentProfile, KCSEResult, StudentInterest,
    UniversityPerformance, AdvisorProfile, AdvisorySession
)


class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    student_id = forms.CharField(max_length=20, label="Student ID / Reg. Number")
    gender = forms.ChoiceField(choices=StudentProfile.GENDER_CHOICES)
    phone_number = forms.CharField(max_length=15, required=False)
    county = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                student_id=self.cleaned_data['student_id'],
                gender=self.cleaned_data['gender'],
                phone_number=self.cleaned_data.get('phone_number', ''),
                county=self.cleaned_data.get('county', ''),
            )
        return user


class AdvisorRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    staff_id = forms.CharField(max_length=20, label="Staff ID")
    department = forms.CharField(max_length=100)
    specialization = forms.CharField(max_length=200, required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    office_location = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            AdvisorProfile.objects.create(
                user=user,
                staff_id=self.cleaned_data['staff_id'],
                department=self.cleaned_data['department'],
                specialization=self.cleaned_data.get('specialization', ''),
                phone_number=self.cleaned_data.get('phone_number', ''),
                office_location=self.cleaned_data.get('office_location', ''),
            )
        return user


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class StudentProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()

    class Meta:
        model = StudentProfile
        fields = ['gender', 'date_of_birth', 'phone_number', 'county',
                  'year_of_study', 'enrollment_year', 'bio']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_id:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.user.first_name = self.cleaned_data['first_name']
            profile.user.last_name = self.cleaned_data['last_name']
            profile.user.email = self.cleaned_data['email']
            profile.user.save()
            profile.save()
        return profile


class KCSEResultForm(forms.ModelForm):
    class Meta:
        model = KCSEResult
        exclude = ['student', 'created_at']
        widgets = {
            'year': forms.NumberInput(attrs={'min': 2000, 'max': 2030}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        grade_choices = [('', '-- Select --')] + list(KCSEResult.GRADE_CHOICES)
        subject_fields = [
            'mathematics', 'english', 'kiswahili', 'biology', 'chemistry',
            'physics', 'history', 'geography', 'business_studies',
            'agriculture', 'computer_studies'
        ]
        for field in subject_fields:
            self.fields[field].choices = grade_choices
            self.fields[field].required = False


class StudentInterestForm(forms.ModelForm):
    class Meta:
        model = StudentInterest
        exclude = ['student', 'updated_at']
        widgets = {
            'career_goal': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your career goals...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        interest_fields = [
            'technology', 'business_finance', 'healthcare', 'education_teaching',
            'agriculture_environment', 'engineering', 'research_science', 'arts_communication'
        ]
        for field in interest_fields:
            self.fields[field].widget = forms.RadioSelect(choices=StudentInterest.INTEREST_LEVEL)
            self.fields[field].label = field.replace('_', ' ').title()


class UniversityPerformanceForm(forms.ModelForm):
    class Meta:
        model = UniversityPerformance
        exclude = ['student', 'created_at']
        widgets = {
            'year': forms.NumberInput(attrs={'min': 2010, 'max': 2030}),
            'semester': forms.NumberInput(attrs={'min': 1, 'max': 3}),
            'marks': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': '0.01'}),
        }


class AdvisorySessionForm(forms.ModelForm):
    class Meta:
        model = AdvisorySession
        fields = ['student', 'scheduled_date', 'notes']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, advisor=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if advisor:
            self.fields['student'].queryset = advisor.assigned_students.all()


class AdvisorNotesForm(forms.ModelForm):
    class Meta:
        model = __import__('dss_guidance.models', fromlist=['Recommendation']).Recommendation
        fields = ['advisor_notes', 'status']
        widgets = {
            'advisor_notes': forms.Textarea(attrs={'rows': 4}),
        }
