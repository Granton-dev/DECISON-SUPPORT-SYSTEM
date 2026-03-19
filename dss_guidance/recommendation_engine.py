"""
DSS Recommendation Engine
Analyzes student KCSE performance, university grades, and interests
to recommend the best-fit academic programs.
"""

GRADE_POINTS = {
    'A': 12, 'A-': 11, 'B+': 10, 'B': 9, 'B-': 8,
    'C+': 7, 'C': 6, 'C-': 5, 'D+': 4, 'D': 3, 'D-': 2, 'E': 1,
}

INTEREST_FIELD_MAP = {
    'computing': ['technology'],
    'business': ['business_finance'],
    'agriculture': ['agriculture_environment'],
    'education': ['education_teaching'],
    'science': ['research_science', 'healthcare'],
    'engineering': ['engineering', 'technology'],
}


def grade_to_points(grade):
    return GRADE_POINTS.get(grade, 0)


def compute_academic_score(student_profile, program):
    """
    Score how well the student's KCSE results match program requirements.
    Returns a score 0–100.
    """
    score = 0
    weight = 0

    # Check if student has KCSE results
    try:
        kcse = student_profile.kcse_result
    except Exception:
        return 0

    # 1. Overall points match (weight: 40)
    max_pts = 84
    student_pts = kcse.total_points
    required_pts = program.minimum_points
    pts_ratio = min(student_pts / max(required_pts, 1), 1.5)
    pts_score = min(pts_ratio * 40, 40)
    score += pts_score
    weight += 40

    # 2. Subject match (weight: 40)
    subject_scores = []
    required_subs = program.get_required_subjects_list()
    subject_map = {
        'Mathematics': kcse.mathematics,
        'English': kcse.english,
        'Kiswahili': kcse.kiswahili,
        'Biology': kcse.biology,
        'Chemistry': kcse.chemistry,
        'Physics': kcse.physics,
        'History': kcse.history,
        'Geography': kcse.geography,
        'Business Studies': kcse.business_studies,
        'Agriculture': kcse.agriculture,
        'Computer Studies': kcse.computer_studies,
    }
    for sub in required_subs:
        for key, val in subject_map.items():
            if sub.lower() in key.lower() and val:
                pts = grade_to_points(val)
                subject_scores.append(pts / 12.0)
                break

    if subject_scores:
        avg_sub = sum(subject_scores) / len(subject_scores)
        score += avg_sub * 40
    else:
        score += 20  # neutral if no required subjects specified
    weight += 40

    # 3. University performance (weight: 20, optional)
    uni_perf = student_profile.university_performance.all()
    if uni_perf.exists():
        uni_grade_map = {
            'A': 1.0, 'B+': 0.85, 'B': 0.75, 'C+': 0.65,
            'C': 0.55, 'D+': 0.45, 'D': 0.35, 'E': 0.2,
        }
        vals = [uni_grade_map.get(p.grade, 0.5) for p in uni_perf]
        avg_uni = sum(vals) / len(vals)
        score += avg_uni * 20
        weight += 20

    # Normalize to 100
    if weight > 0:
        score = (score / weight) * 100
    return round(score, 2)


def compute_interest_score(student_profile, program):
    """
    Score how well the student's interests align with the program's faculty.
    Returns a score 0–100.
    """
    try:
        interests = student_profile.interests
    except Exception:
        return 50  # neutral

    faculty = program.faculty
    relevant_fields = INTEREST_FIELD_MAP.get(faculty, [])

    if not relevant_fields:
        return 50

    scores = []
    for field in relevant_fields:
        val = getattr(interests, field, 3)
        scores.append((val / 5.0) * 100)

    return round(sum(scores) / len(scores), 2)


def compute_match_score(student_profile, program):
    """
    Combined match score: 60% academic, 40% interest.
    Returns score 0–100 and a reasoning string.
    """
    academic = compute_academic_score(student_profile, program)
    interest = compute_interest_score(student_profile, program)

    combined = (academic * 0.6) + (interest * 0.4)

    reasoning_parts = []

    # Academic assessment
    try:
        kcse = student_profile.kcse_result
        if kcse.total_points >= program.minimum_points:
            reasoning_parts.append(
                f"Your KCSE score of {kcse.total_points} points meets the "
                f"minimum requirement of {program.minimum_points} points for this program."
            )
        else:
            gap = program.minimum_points - kcse.total_points
            reasoning_parts.append(
                f"Your KCSE score of {kcse.total_points} points is {gap} points below "
                f"the minimum requirement of {program.minimum_points} for this program."
            )
    except Exception:
        reasoning_parts.append("No KCSE results on record.")

    # Interest assessment
    if interest >= 70:
        reasoning_parts.append(
            f"Your stated interests strongly align with the {program.get_faculty_display()} field."
        )
    elif interest >= 50:
        reasoning_parts.append(
            f"Your interests moderately align with the {program.get_faculty_display()} field."
        )
    else:
        reasoning_parts.append(
            f"Your stated interests show limited alignment with the "
            f"{program.get_faculty_display()} field."
        )

    # Career paths note
    careers = program.get_career_paths_list()
    if careers:
        reasoning_parts.append(
            f"This program leads to careers such as: {', '.join(careers[:4])}."
        )

    reasoning = " ".join(reasoning_parts)
    return round(combined, 2), reasoning


def generate_recommendations(student_profile, top_n=5):
    """
    Generate top N program recommendations for a student.
    Returns a list of dicts sorted by match score descending.
    """
    from .models import AcademicProgram, Recommendation

    programs = AcademicProgram.objects.filter(is_active=True)
    results = []

    for program in programs:
        score, reasoning = compute_match_score(student_profile, program)
        results.append({
            'program': program,
            'score': score,
            'reasoning': reasoning,
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    top_results = results[:top_n]

    # Save recommendations to DB (delete old ones first)
    Recommendation.objects.filter(student=student_profile, status='pending').delete()

    saved = []
    for item in top_results:
        rec = Recommendation.objects.create(
            student=student_profile,
            program=item['program'],
            match_score=item['score'],
            reasoning=item['reasoning'],
            status='pending',
        )
        saved.append(rec)

    return saved
