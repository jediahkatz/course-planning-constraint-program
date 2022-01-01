from cp2_types import CourseInfo
import pytest

@pytest.fixture
def sample_courses_info() -> list[CourseInfo]:
    return [
        {
            'id': 'CIS-120',
            'title': 'Programming Languages & Techniques I',
            'semester': '2022A',
            'prerequisites': [],
            'requirements': [
                {
                    "id": "MFR@SAS",
                    "code": "MFR",
                    "school": "SAS",
                    "semester": "2022A",
                    "name": "Formal Reasoning Course"
                },
                {
                    "id": "ENG@SEAS",
                    "code": "ENG",
                    "school": "SEAS",
                    "semester": "2022A",
                    "name": "Engineering"
                }
            ],
            'crosslistings': [],
            'sections': [],
            'course_quality': None,
            'instructor_quality': None,
            'difficulty': None,
            'work_required': None,
        },
        {
            'id': 'CIS-160',
            'title': 'Mathematical Foundations of Computer Science',
            'semester': '2022A',
            'prerequisites': [],
            'requirements': [
                {
                    "id": "MATH@SEAS",
                    "code": "MATH",
                    "school": "SEAS",
                    "semester": "2022A",
                    "name": "Mathematics"
                }
            ],
            'crosslistings': [],
            'sections': [],
            'course_quality': None,
            'instructor_quality': None,
            'difficulty': None,
            'work_required': None,
        },
        {
            'id': 'CIS-121',
            'title': 'Programming Languages & Techniques II',
            'semester': '2022A',
            'prerequisites': [['CIS-120'], ['CIS-160']],
            'requirements': [
                {
                    "id": "ENG@SEAS",
                    "code": "ENG",
                    "school": "SEAS",
                    "semester": "2022A",
                    "name": "Engineering"
                }
            ],
            'crosslistings': [],
            'sections': [],
            'course_quality': None,
            'instructor_quality': None,
            'difficulty': None,
            'work_required': None,
        },
        {
            'id': 'CIS-262',
            'title': 'Automata, Computability, and Complexity',
            'semester': '2022A',
            'prerequisites': [['CIS-160']],
            'requirements': [
                {
                    "id": "MATH@SEAS",
                    "code": "MATH",
                    "school": "SEAS",
                    "semester": "2022A",
                    "name": "Mathematics"
                }
            ],
            'crosslistings': [],
            'sections': [],
            'course_quality': None,
            'instructor_quality': None,
            'difficulty': None,
            'work_required': None,
        },
        {
            "id": "MATH-104",
            "title": "Calculus, Part I",
            "semester": "2022A",
            "prerequisites": [],
            "requirements": [
                {
                    "id": "MFR@SAS",
                    "code": "MFR",
                    "school": "SAS",
                    "semester": "2022A",
                    "name": "Formal Reasoning Course"
                },
                {
                    "id": "MATH@SEAS",
                    "code": "MATH",
                    "school": "SEAS",
                    "semester": "2022A",
                    "name": "Mathematics"
                },
                {
                    "id": "FGE@WH",
                    "code": "FGE",
                    "school": "WH",
                    "semester": "2022A",
                    "name": "Flex Gen Ed"
                }
            ],
            "crosslistings": [],
            "sections": [],
            "course_quality": None,
            "instructor_quality": None,
            "difficulty": None,
            "work_required": None,
        }
    ]
