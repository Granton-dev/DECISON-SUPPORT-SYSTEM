# DSS Academic Guidance System — University of Embu
### Django Implementation

---

## Project Structure

```
dss_project/
├── manage.py
├── requirements.txt
├── dss_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── dss_guidance/
    ├── models.py              # All database models
    ├── views.py               # All views (student, advisor, shared)
    ├── urls.py                # URL routing
    ├── forms.py               # All Django forms
    ├── admin.py               # Admin panel configuration
    ├── recommendation_engine.py  # DSS recommendation logic
    ├── management/
    │   └── commands/
    │       └── seed_programs.py  # Seeds 10 sample programs
    └── templates/
        └── dss_guidance/
            ├── base.html
            ├── auth/
            │   ├── login.html
            │   ├── register_student.html
            │   └── register_advisor.html
            ├── student/
            │   ├── dashboard.html
            │   ├── profile_edit.html
            │   ├── kcse_results.html
            │   ├── interests.html
            │   ├── uni_performance.html
            │   └── recommendations.html
            ├── advisor/
            │   ├── dashboard.html
            │   ├── students.html
            │   ├── student_detail.html
            │   ├── review_recommendation.html
            │   ├── schedule_session.html
            │   └── reports.html
            └── shared/
                ├── program_list.html
                └── program_detail.html
```

---

## Setup Instructions

### 1. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run database migrations

```bash
python manage.py makemigrations dss_guidance
python manage.py migrate
```

### 4. Seed sample academic programs

```bash
python manage.py seed_programs
```

This loads 10 real University of Embu-relevant programs:
- BSc Computer Science, BSc Information Technology
- Bachelor of Commerce, BBA
- BSc Agriculture
- BEd Arts, BEd Science
- BSc Nursing, BSc Environmental Science
- BE Civil Engineering

### 5. Create a superuser (admin)

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

Open your browser at: **http://127.0.0.1:8000/**

---

## User Roles & Access

| Role     | Registration URL         | Dashboard URL           |
|----------|--------------------------|-------------------------|
| Student  | `/register/student/`     | `/student/dashboard/`   |
| Advisor  | `/register/advisor/`     | `/advisor/dashboard/`   |
| Admin    | `/admin/`                | Django Admin Panel      |

---

## How to Assign Students to Advisors

1. Go to **http://127.0.0.1:8000/admin/**
2. Click **Advisor Profiles**
3. Select an advisor
4. Under "Assigned Students", add students using the horizontal filter widget
5. Save

---

## How the Recommendation Engine Works

The engine (`recommendation_engine.py`) scores each active program for a student using:

| Factor                   | Weight |
|--------------------------|--------|
| KCSE overall points      | 40%    |
| KCSE subject match       | 40%    |
| Career interest survey   | 40%*  |
| University performance   | 20%*  |

*Combined academic (60%) + interest (40%) final score*

**To generate recommendations:**
1. Student logs in
2. Enters KCSE results (`/student/kcse/`)
3. Completes interest survey (`/student/interests/`)
4. Clicks "Generate Recommendations" on dashboard

---

## Key Features

### Students
- Register and create profile
- Enter KCSE results with subject grades
- Complete career interest survey (8 fields, 1–5 scale)
- Add university unit grades
- Generate AI-powered program recommendations
- Accept or decline recommendations
- View advisory sessions

### Advisors
- View all assigned students
- See full student profiles, KCSE data, interests, and grades
- Review and annotate recommendations
- Schedule advisory sessions
- View reports and analytics (program demand, faculty distribution)

### Admin
- Full control via Django Admin
- Manage programs, students, advisors, recommendations, sessions
- Assign students to advisors

---

## Requirements

```
Django>=4.2
```

---

## Technologies

- **Backend:** Django 4.x (Python)
- **Database:** SQLite (default) — switchable to PostgreSQL/MySQL
- **Frontend:** Bootstrap 5.3 + Bootstrap Icons
- **Charts:** CSS progress bars (no external charting library needed)

---

## Notes

- Change `SECRET_KEY` in `settings.py` before deploying to production
- Set `DEBUG = False` in production
- Run `python manage.py collectstatic` before deploying
