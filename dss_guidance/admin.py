from django.contrib import admin
from .models import (
    AcademicProgram, StudentProfile, KCSEResult,
    UniversityPerformance, StudentInterest, Recommendation,
    AdvisorProfile, AdvisorySession
)


@admin.register(AcademicProgram)
class AcademicProgramAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'faculty', 'minimum_grade', 'minimum_points', 'duration_years', 'is_active']
    list_filter = ['faculty', 'is_active']
    search_fields = ['name', 'code']
    list_editable = ['is_active']


class KCSEInline(admin.StackedInline):
    model = KCSEResult
    extra = 0


class InterestInline(admin.StackedInline):
    model = StudentInterest
    extra = 0


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'get_full_name', 'gender', 'current_program', 'year_of_study', 'enrollment_year']
    list_filter = ['gender', 'year_of_study', 'current_program__faculty']
    search_fields = ['student_id', 'user__first_name', 'user__last_name', 'user__email']
    inlines = [KCSEInline, InterestInline]

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'


@admin.register(KCSEResult)
class KCSEResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'index_number', 'year', 'overall_grade', 'total_points']
    list_filter = ['year', 'overall_grade']
    search_fields = ['student__student_id', 'index_number']


@admin.register(UniversityPerformance)
class UniversityPerformanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'unit_code', 'unit_name', 'year', 'semester', 'grade', 'marks']
    list_filter = ['year', 'semester', 'grade']
    search_fields = ['student__student_id', 'unit_code', 'unit_name']


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['student', 'program', 'match_score', 'status', 'reviewed_by', 'created_at']
    list_filter = ['status', 'program__faculty']
    search_fields = ['student__student_id', 'program__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AdvisorProfile)
class AdvisorProfileAdmin(admin.ModelAdmin):
    list_display = ['staff_id', 'get_full_name', 'department', 'specialization', 'get_student_count']
    search_fields = ['staff_id', 'user__first_name', 'user__last_name', 'department']
    filter_horizontal = ['assigned_students']

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'

    def get_student_count(self, obj):
        return obj.assigned_students.count()
    get_student_count.short_description = 'Assigned Students'


@admin.register(AdvisorySession)
class AdvisorySessionAdmin(admin.ModelAdmin):
    list_display = ['advisor', 'student', 'scheduled_date', 'status']
    list_filter = ['status']
    search_fields = ['advisor__staff_id', 'student__student_id']


admin.site.site_header = "University of Embu – DSS Admin"
admin.site.site_title = "DSS Admin"
admin.site.index_title = "Academic Guidance & Career Advisory System"
