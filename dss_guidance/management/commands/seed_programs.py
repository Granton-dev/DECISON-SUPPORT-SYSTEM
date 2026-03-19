"""
Management command to seed the database with sample academic programs.
Run with: python manage.py seed_programs
"""
from django.core.management.base import BaseCommand
from dss_guidance.models import AcademicProgram


PROGRAMS = [
    {
        "name": "Bachelor of Science in Computer Science",
        "code": "BSC-CS",
        "faculty": "computing",
        "description": "A comprehensive program covering software development, algorithms, data structures, artificial intelligence, and computer systems design.",
        "duration_years": 4,
        "minimum_grade": "B",
        "minimum_points": 60,
        "required_subjects": "Mathematics, English, Physics, Computer Studies",
        "skills_developed": "Programming, Problem Solving, Software Engineering, Data Analysis, Networking",
        "career_paths": "Software Developer, Data Scientist, Systems Analyst, IT Consultant, Cybersecurity Analyst",
    },
    {
        "name": "Bachelor of Science in Information Technology",
        "code": "BSC-IT",
        "faculty": "computing",
        "description": "Focuses on IT infrastructure, networking, database management, and enterprise systems.",
        "duration_years": 4,
        "minimum_grade": "C+",
        "minimum_points": 52,
        "required_subjects": "Mathematics, English, Computer Studies",
        "skills_developed": "Networking, Database Administration, System Support, Web Development",
        "career_paths": "IT Manager, Network Administrator, Database Administrator, Web Developer",
    },
    {
        "name": "Bachelor of Commerce",
        "code": "BCOM",
        "faculty": "business",
        "description": "Covers accounting, finance, marketing, human resources, and business strategy.",
        "duration_years": 4,
        "minimum_grade": "C+",
        "minimum_points": 50,
        "required_subjects": "Mathematics, English, Business Studies",
        "skills_developed": "Accounting, Financial Analysis, Marketing, Leadership, Strategic Planning",
        "career_paths": "Accountant, Financial Analyst, Marketing Manager, HR Officer, Business Consultant",
    },
    {
        "name": "Bachelor of Business Administration",
        "code": "BBA",
        "faculty": "business",
        "description": "A broad business degree covering entrepreneurship, management, and organizational behavior.",
        "duration_years": 4,
        "minimum_grade": "C+",
        "minimum_points": 48,
        "required_subjects": "Mathematics, English, Business Studies",
        "skills_developed": "Management, Entrepreneurship, Communication, Decision Making",
        "career_paths": "Business Manager, Entrepreneur, Operations Manager, Project Manager",
    },
    {
        "name": "Bachelor of Science in Agriculture",
        "code": "BSC-AGRIC",
        "faculty": "agriculture",
        "description": "Covers crop science, soil science, animal husbandry, agribusiness, and agricultural extension.",
        "duration_years": 4,
        "minimum_grade": "C+",
        "minimum_points": 46,
        "required_subjects": "Biology, Chemistry, Agriculture, Mathematics",
        "skills_developed": "Crop Management, Soil Analysis, Agribusiness, Research, Extension Services",
        "career_paths": "Agronomist, Agricultural Officer, Farm Manager, Agribusiness Manager, Researcher",
    },
    {
        "name": "Bachelor of Education (Arts)",
        "code": "BED-ARTS",
        "faculty": "education",
        "description": "Trains teachers in arts subjects including English, History, Geography, and CRE.",
        "duration_years": 4,
        "minimum_grade": "C+",
        "minimum_points": 48,
        "required_subjects": "English, Kiswahili, History, Geography",
        "skills_developed": "Teaching, Curriculum Development, Communication, Research, Mentorship",
        "career_paths": "Secondary Teacher, Education Officer, Curriculum Developer, Instructional Designer",
    },
    {
        "name": "Bachelor of Education (Science)",
        "code": "BED-SCI",
        "faculty": "education",
        "description": "Prepares science and mathematics teachers for secondary schools.",
        "duration_years": 4,
        "minimum_grade": "C+",
        "minimum_points": 50,
        "required_subjects": "Mathematics, Biology, Chemistry, Physics",
        "skills_developed": "Science Teaching, Laboratory Skills, Curriculum Development, Mentorship",
        "career_paths": "Science Teacher, Mathematics Teacher, Education Researcher, School Administrator",
    },
    {
        "name": "Bachelor of Science in Nursing",
        "code": "BSC-NURS",
        "faculty": "science",
        "description": "Comprehensive nursing training covering clinical care, community health, and medical ethics.",
        "duration_years": 4,
        "minimum_grade": "B-",
        "minimum_points": 56,
        "required_subjects": "Biology, Chemistry, Mathematics, English",
        "skills_developed": "Patient Care, Clinical Assessment, Medical Knowledge, Communication, Ethics",
        "career_paths": "Registered Nurse, Community Health Worker, Nursing Officer, Health Educator",
    },
    {
        "name": "Bachelor of Science in Environmental Science",
        "code": "BSC-ENV",
        "faculty": "science",
        "description": "Covers ecology, environmental management, climate change, and conservation.",
        "duration_years": 4,
        "minimum_grade": "C+",
        "minimum_points": 50,
        "required_subjects": "Biology, Chemistry, Geography, Mathematics",
        "skills_developed": "Environmental Analysis, Research, Conservation, Data Collection, Policy Analysis",
        "career_paths": "Environmental Officer, Conservation Scientist, Climate Researcher, Environmental Consultant",
    },
    {
        "name": "Bachelor of Engineering in Civil Engineering",
        "code": "BE-CIVIL",
        "faculty": "engineering",
        "description": "Covers structural engineering, water resources, transport, and construction management.",
        "duration_years": 5,
        "minimum_grade": "B",
        "minimum_points": 62,
        "required_subjects": "Mathematics, Physics, Chemistry, English",
        "skills_developed": "Structural Design, Project Management, AutoCAD, Materials Science, Surveying",
        "career_paths": "Civil Engineer, Structural Engineer, Project Manager, Urban Planner, Site Engineer",
    },
]


class Command(BaseCommand):
    help = "Seed the database with sample academic programs for University of Embu DSS"

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for data in PROGRAMS:
            obj, was_created = AcademicProgram.objects.update_or_create(
                code=data['code'],
                defaults=data
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Created {created} programs, updated {updated} programs."
            )
        )
