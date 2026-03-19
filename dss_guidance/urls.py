from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/student/', views.register_student, name='register_student'),
    path('register/advisor/', views.register_advisor, name='register_advisor'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Student
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/edit/', views.student_profile_edit, name='student_profile_edit'),
    path('student/kcse/', views.kcse_results, name='kcse_results'),
    path('student/interests/', views.student_interests, name='student_interests'),
    path('student/performance/', views.university_performance, name='university_performance'),
    path('student/recommendations/', views.view_recommendations, name='view_recommendations'),
    path('student/recommendations/generate/', views.get_recommendations, name='get_recommendations'),
    path('student/recommendations/<int:rec_id>/respond/', views.recommendation_response, name='recommendation_response'),

    # Advisor
    path('advisor/dashboard/', views.advisor_dashboard, name='advisor_dashboard'),
    path('advisor/students/', views.advisor_students, name='advisor_students'),
    path('advisor/students/<int:student_id>/', views.advisor_student_detail, name='advisor_student_detail'),
    path('advisor/recommendations/<int:rec_id>/review/', views.review_recommendation, name='review_recommendation'),
    path('advisor/sessions/schedule/', views.schedule_session, name='schedule_session'),
    path('advisor/reports/', views.advisor_reports, name='advisor_reports'),

    # Shared
    path('programs/', views.program_list, name='program_list'),
    path('programs/<int:pk>/', views.program_detail, name='program_detail'),
]
