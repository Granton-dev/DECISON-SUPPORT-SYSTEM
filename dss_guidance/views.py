from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from django.http import HttpResponseForbidden

from .models import (
    StudentProfile, AdvisorProfile, AcademicProgram,
    KCSEResult, StudentInterest, UniversityPerformance,
    Recommendation, AdvisorySession
)
from .forms import (
    StudentRegistrationForm, AdvisorRegistrationForm, CustomLoginForm,
    StudentProfileForm, KCSEResultForm, StudentInterestForm,
    UniversityPerformanceForm, AdvisorySessionForm, AdvisorNotesForm
)
from .recommendation_engine import generate_recommendations


# ─── Auth helpers ────────────────────────────────────────────────────────────

def is_student(user):
    return hasattr(user, 'student_profile')

def is_advisor(user):
    return hasattr(user, 'advisor_profile')


# ─── Auth Views ──────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = CustomLoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f"Welcome back, {user.first_name}!")
        return redirect('dashboard')
    return render(request, 'dss_guidance/auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


def register_student(request):
    form = StudentRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created successfully! Complete your profile to get started.")
        return redirect('student_profile_edit')
    return render(request, 'dss_guidance/auth/register_student.html', {'form': form})


def register_advisor(request):
    form = AdvisorRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Advisor account created successfully!")
        return redirect('advisor_dashboard')
    return render(request, 'dss_guidance/auth/register_advisor.html', {'form': form})


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    if request.user.is_superuser:
        return redirect('/admin/')
    if is_student(request.user):
        return redirect('student_dashboard')
    if is_advisor(request.user):
        return redirect('advisor_dashboard')
    return redirect('login')


# ─── Student Views ────────────────────────────────────────────────────────────

@login_required
def student_dashboard(request):
    if not is_student(request.user):
        return HttpResponseForbidden()
    student = request.user.student_profile
    recommendations = student.recommendations.select_related('program').order_by('-match_score')[:5]
    sessions = student.sessions.select_related('advisor__user').order_by('-scheduled_date')[:5]
    has_kcse = hasattr(student, 'kcse_result')
    has_interests = hasattr(student, 'interests')
    context = {
        'student': student,
        'recommendations': recommendations,
        'sessions': sessions,
        'has_kcse': has_kcse,
        'has_interests': has_interests,
        'profile_complete': has_kcse and has_interests,
    }
    return render(request, 'dss_guidance/student/dashboard.html', context)


@login_required
def student_profile_edit(request):
    if not is_student(request.user):
        return HttpResponseForbidden()
    student = request.user.student_profile
    form = StudentProfileForm(request.POST or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('student_dashboard')
    return render(request, 'dss_guidance/student/profile_edit.html', {'form': form, 'student': student})


@login_required
def kcse_results(request):
    if not is_student(request.user):
        return HttpResponseForbidden()
    student = request.user.student_profile
    instance = KCSEResult.objects.filter(student=student).first()
    form = KCSEResultForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        kcse = form.save(commit=False)
        kcse.student = student
        kcse.save()
        messages.success(request, "KCSE results saved.")
        return redirect('student_interests')
    return render(request, 'dss_guidance/student/kcse_results.html', {'form': form, 'instance': instance})


@login_required
def student_interests(request):
    if not is_student(request.user):
        return HttpResponseForbidden()
    student = request.user.student_profile
    instance = StudentInterest.objects.filter(student=student).first()
    form = StudentInterestForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        interest = form.save(commit=False)
        interest.student = student
        interest.save()
        messages.success(request, "Interests saved.")
        return redirect('student_dashboard')
    return render(request, 'dss_guidance/student/interests.html', {'form': form})


@login_required
def university_performance(request):
    if not is_student(request.user):
        return HttpResponseForbidden()
    student = request.user.student_profile
    performance = student.university_performance.all().order_by('year', 'semester')
    form = UniversityPerformanceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        perf = form.save(commit=False)
        perf.student = student
        perf.save()
        messages.success(request, "Unit grade added.")
        return redirect('university_performance')
    return render(request, 'dss_guidance/student/uni_performance.html', {
        'form': form, 'performance': performance
    })


@login_required
def get_recommendations(request):
    if not is_student(request.user):
        return HttpResponseForbidden()
    student = request.user.student_profile
    if not hasattr(student, 'kcse_result'):
        messages.warning(request, "Please enter your KCSE results before generating recommendations.")
        return redirect('kcse_results')
    if not hasattr(student, 'interests'):
        messages.warning(request, "Please complete your interest survey before generating recommendations.")
        return redirect('student_interests')
    recs = generate_recommendations(student, top_n=6)
    messages.success(request, f"Generated {len(recs)} program recommendations based on your profile.")
    return redirect('view_recommendations')


@login_required
def view_recommendations(request):
    if not is_student(request.user):
        return HttpResponseForbidden()
    student = request.user.student_profile
    recommendations = student.recommendations.select_related('program').order_by('-match_score')
    return render(request, 'dss_guidance/student/recommendations.html', {
        'recommendations': recommendations,
        'student': student,
    })


@login_required
def recommendation_response(request, rec_id):
    if not is_student(request.user):
        return HttpResponseForbidden()
    rec = get_object_or_404(Recommendation, id=rec_id, student=request.user.student_profile)
    action = request.POST.get('action')
    if action == 'accept':
        rec.status = 'accepted'
        rec.save()
        messages.success(request, f"You accepted the recommendation for {rec.program.name}.")
    elif action == 'decline':
        rec.status = 'declined'
        rec.save()
        messages.info(request, f"You declined the recommendation for {rec.program.name}.")
    return redirect('view_recommendations')


# ─── Advisor Views ────────────────────────────────────────────────────────────

@login_required
def advisor_dashboard(request):
    if not is_advisor(request.user):
        return HttpResponseForbidden()
    advisor = request.user.advisor_profile
    students = advisor.assigned_students.select_related('user', 'kcse_result').all()
    pending_recs = Recommendation.objects.filter(
        student__in=students, status='pending'
    ).select_related('student__user', 'program').order_by('-created_at')[:10]
    upcoming_sessions = advisor.sessions.filter(status='scheduled').order_by('scheduled_date')[:5]
    context = {
        'advisor': advisor,
        'students': students,
        'pending_recs': pending_recs,
        'upcoming_sessions': upcoming_sessions,
        'total_students': students.count(),
        'pending_count': pending_recs.count(),
    }
    return render(request, 'dss_guidance/advisor/dashboard.html', context)


@login_required
def advisor_students(request):
    if not is_advisor(request.user):
        return HttpResponseForbidden()
    advisor = request.user.advisor_profile
    students = advisor.assigned_students.select_related('user', 'current_program').all()
    return render(request, 'dss_guidance/advisor/students.html', {
        'advisor': advisor, 'students': students
    })


@login_required
def advisor_student_detail(request, student_id):
    if not is_advisor(request.user):
        return HttpResponseForbidden()
    advisor = request.user.advisor_profile
    student = get_object_or_404(StudentProfile, id=student_id)
    if student not in advisor.assigned_students.all():
        return HttpResponseForbidden("This student is not assigned to you.")
    kcse = KCSEResult.objects.filter(student=student).first()
    interests = StudentInterest.objects.filter(student=student).first()
    performance = student.university_performance.all().order_by('year', 'semester')
    recommendations = student.recommendations.select_related('program').order_by('-match_score')
    return render(request, 'dss_guidance/advisor/student_detail.html', {
        'student': student, 'kcse': kcse, 'interests': interests,
        'performance': performance, 'recommendations': recommendations,
        'advisor': advisor,
    })


@login_required
def review_recommendation(request, rec_id):
    if not is_advisor(request.user):
        return HttpResponseForbidden()
    rec = get_object_or_404(Recommendation, id=rec_id)
    form = AdvisorNotesForm(request.POST or None, instance=rec)
    if request.method == 'POST' and form.is_valid():
        reviewed = form.save(commit=False)
        reviewed.reviewed_by = request.user
        reviewed.status = 'reviewed'
        reviewed.save()
        messages.success(request, "Recommendation reviewed.")
        return redirect('advisor_student_detail', student_id=rec.student.id)
    return render(request, 'dss_guidance/advisor/review_recommendation.html', {
        'rec': rec, 'form': form
    })


@login_required
def schedule_session(request):
    if not is_advisor(request.user):
        return HttpResponseForbidden()
    advisor = request.user.advisor_profile
    form = AdvisorySessionForm(advisor=advisor, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        session = form.save(commit=False)
        session.advisor = advisor
        session.save()
        messages.success(request, "Session scheduled successfully.")
        return redirect('advisor_dashboard')
    return render(request, 'dss_guidance/advisor/schedule_session.html', {
        'form': form, 'advisor': advisor
    })


@login_required
def advisor_reports(request):
    if not is_advisor(request.user):
        return HttpResponseForbidden()
    advisor = request.user.advisor_profile
    students = advisor.assigned_students.all()

    # Stats
    total_students = students.count()
    students_with_kcse = KCSEResult.objects.filter(student__in=students).count()
    students_with_interests = StudentInterest.objects.filter(student__in=students).count()
    total_recs = Recommendation.objects.filter(student__in=students).count()
    accepted_recs = Recommendation.objects.filter(student__in=students, status='accepted').count()

    # Program demand
    program_demand = Recommendation.objects.filter(
        student__in=students
    ).values('program__name').annotate(count=Count('id')).order_by('-count')[:8]

    # Faculty distribution
    from django.db.models import F
    faculty_dist = AcademicProgram.objects.filter(
        recommendations__student__in=students
    ).values('faculty').annotate(count=Count('recommendations')).order_by('-count')

    context = {
        'advisor': advisor,
        'total_students': total_students,
        'students_with_kcse': students_with_kcse,
        'students_with_interests': students_with_interests,
        'total_recs': total_recs,
        'accepted_recs': accepted_recs,
        'program_demand': program_demand,
        'faculty_dist': faculty_dist,
    }
    return render(request, 'dss_guidance/advisor/reports.html', context)


# ─── Shared Views ─────────────────────────────────────────────────────────────

@login_required
def program_list(request):
    faculty = request.GET.get('faculty', '')
    programs = AcademicProgram.objects.filter(is_active=True)
    if faculty:
        programs = programs.filter(faculty=faculty)
    faculties = AcademicProgram.FACULTY_CHOICES
    return render(request, 'dss_guidance/shared/program_list.html', {
        'programs': programs, 'faculties': faculties, 'selected_faculty': faculty
    })


@login_required
def program_detail(request, pk):
    program = get_object_or_404(AcademicProgram, pk=pk, is_active=True)
    return render(request, 'dss_guidance/shared/program_detail.html', {'program': program})
