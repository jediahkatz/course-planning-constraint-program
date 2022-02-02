from cp2_types import CourseInfo, Semester
import pytest

@pytest.fixture
def sample_courses_info() -> list[CourseInfo]:
    return [
        {
            'id': 'CIS-120',
            'title': 'Programming Languages & Techniques I',
            'credits': 1.0,
            'semester': '2022A',
            'prerequisites': [],
            'requirements': [
                {
                    'id': 'MFR@SAS',
                    'code': 'MFR',
                    'school': 'SAS',
                    'semester': '2022A',
                    'name': 'Formal Reasoning Course'
                },
                {
                    'id': 'ENG@SEAS',
                    'code': 'ENG',
                    'school': 'SEAS',
                    'semester': '2022A',
                    'name': 'Engineering'
                }
            ],
            'rate_offered': {
                Semester.FALL.value: 1,
                Semester.SPRING.value: 1,
                Semester.SUMMER.value: 1,
            },
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
            'credits': 1.0,
            'semester': '2022A',
            'prerequisites': [],
            'requirements': [
                {
                    'id': 'MATH@SEAS',
                    'code': 'MATH',
                    'school': 'SEAS',
                    'semester': '2022A',
                    'name': 'Mathematics'
                }
            ],
            'rate_offered': {
                Semester.FALL.value: 1,
                Semester.SPRING.value: 1,
                Semester.SUMMER.value: 1,
            },
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
            'credits': 1.0,
            'semester': '2022A',
            'prerequisites': [['CIS-120'], ['CIS-160']],
            'requirements': [
                {
                    'id': 'ENG@SEAS',
                    'code': 'ENG',
                    'school': 'SEAS',
                    'semester': '2022A',
                    'name': 'Engineering'
                }
            ],
            'rate_offered': {
                Semester.FALL.value: 1,
                Semester.SPRING.value: 1,
                Semester.SUMMER.value: 1,
            },
            'crosslistings': [],
            'sections': [],
            'course_quality': None,
            'instructor_quality': None,
            'difficulty': None,
            'work_required': None,
        },
        {
            'id': 'CIS-240',
            'title': 'Computer Organization and Design',
            'credits': 1.0,
            'semester': '2022A',
            'prerequisites': [['CIS-120']],
            'requirements': [
                {
                    'id': 'ENG@SEAS',
                    'code': 'ENG',
                    'school': 'SEAS',
                    'semester': '2022A',
                    'name': 'Engineering'
                }
            ],
            'rate_offered': {
                Semester.FALL.value: 1,
                Semester.SPRING.value: 1,
                Semester.SUMMER.value: 1,
            },
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
            'credits': 1.0,
            'semester': '2022A',
            'prerequisites': [['CIS-160']],
            'requirements': [
                {
                    'id': 'MATH@SEAS',
                    'code': 'MATH',
                    'school': 'SEAS',
                    'semester': '2022A',
                    'name': 'Mathematics'
                }
            ],
            'rate_offered': {
                Semester.FALL.value: 1,
                Semester.SPRING.value: 1,
                Semester.SUMMER.value: 1,
            },
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
            'credits': 1.0,
            'semester': '2022A',
            'prerequisites': [['CIS-160']],
            'requirements': [
                {
                    'id': 'MATH@SEAS',
                    'code': 'MATH',
                    'school': 'SEAS',
                    'semester': '2022A',
                    'name': 'Mathematics'
                }
            ],
            'rate_offered': {
                Semester.FALL.value: 1,
                Semester.SPRING.value: 1,
                Semester.SUMMER.value: 1,
            },
            'crosslistings': [],
            'sections': [],
            'course_quality': None,
            'instructor_quality': None,
            'difficulty': None,
            'work_required': None,
        },
        {
            'id': 'MATH-104',
            'title': 'Calculus, Part I',
            'credits': 1.0,
            'semester': '2022A',
            'prerequisites': [],
            'requirements': [
                {
                    'id': 'MFR@SAS',
                    'code': 'MFR',
                    'school': 'SAS',
                    'semester': '2022A',
                    'name': 'Formal Reasoning Course'
                },
                {
                    'id': 'MATH@SEAS',
                    'code': 'MATH',
                    'school': 'SEAS',
                    'semester': '2022A',
                    'name': 'Mathematics'
                },
                {
                    'id': 'FGE@WH',
                    'code': 'FGE',
                    'school': 'WH',
                    'semester': '2022A',
                    'name': 'Flex Gen Ed'
                }
            ],
            'rate_offered': {
                Semester.FALL.value: 1,
                Semester.SPRING.value: 1,
                Semester.SUMMER.value: 1,
            },
            'crosslistings': [],
            'sections': [],
            'course_quality': None,
            'instructor_quality': None,
            'difficulty': None,
            'work_required': None,
        },
        {
            'id': 'CIS-261',
            'title': 'Discrete Probability',
            'credits': 1.0,
            'semester': '2022A',
            'prerequisites': [['CIS-160']],
            'rate_offered': {
                Semester.FALL.value: 1,
                Semester.SPRING.value: 0,
                Semester.SUMMER.value: 0,
            },
            'course_quality': 2.84,
            'instructor_quality': 3.141,
            'difficulty': 3.511,
            'work_required': 3.14,
            'crosslistings': [],
            'requirements': [
                {
                    'id': 'ENG@SEAS',
                    'code': 'ENG',
                    'school': 'SEAS',
                    'semester': '2022A',
                    'name': 'Engineering'
                }
            ],
            'sections': [],
        },
        {
            'id': 'CIS-188',
            'title': 'DevOps',
            'credits': 0.5,
            'semester': '2022A',
            'prerequisites': [],
            'requirements': [
                {
                    'id': 'ENG@SEAS',
                    'code': 'ENG',
                    'school': 'SEAS',
                    'semester': '2022A',
                    'name': 'Engineering'
                }
            ],
            'rate_offered': {
                Semester.FALL.value: 1,
                Semester.SPRING.value: 1,
                Semester.SUMMER.value: 1,
            },
            'crosslistings': [],
            'sections': [],
            'course_quality': None,
            'instructor_quality': None,
            'difficulty': None,
            'work_required': None,
        },
        {
            'id': 'CIS-189',
            'title': 'Solving Hard Problems in Practice',
            'credits': 0.5,
            'semester': '2022A',
            'prerequisites': [],
            'requirements': [
                {
                    'id': 'ENG@SEAS',
                    'code': 'ENG',
                    'school': 'SEAS',
                    'semester': '2022A',
                    'name': 'Engineering'
                }
            ],
            'rate_offered': {
                Semester.FALL.value: 1,
                Semester.SPRING.value: 1,
                Semester.SUMMER.value: 1,
            },
            'crosslistings': [],
            'sections': [],
            'course_quality': None,
            'instructor_quality': None,
            'difficulty': None,
            'work_required': None,
        },
    ]
