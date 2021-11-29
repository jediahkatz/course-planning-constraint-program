# Idea: schedule generator, works like color palette generator (coolors.co)
# Later can expand to 4yr plan

from typing import Optional
from cp2_types import CourseRequest, Index, CourseInfo, Requirement, RequirementBlock, ScheduleParams
from fetch_data import fetch_course_infos
from solver import generate_schedule

NUM_SEMESTERS = 8
MAX_COURSES_PER_SEMESTER = 6

CIS_BSE: RequirementBlock = [
    # === ENGINEERING ===
    Requirement(courses=['CIS-110']),
    Requirement(courses=['CIS-120']),
    Requirement(courses=['CIS-121']),
    Requirement(courses=['CIS-240']),
    Requirement(courses=['CIS-262']),
    Requirement(courses=['CIS-320']),
    Requirement(courses=['CIS-380']),
    Requirement(courses=['CIS-400', 'CIS-410']),
    Requirement(courses=['CIS-401', 'CIS-411']),
    Requirement(courses=['CIS-471']),
    # cis electives
    *([Requirement(
        categories=['ENG@SEAS'], 
        depts=['CIS', 'NETS'], 
        min_number=200,
        max_number=699,
        nickname="CIS Elective"
    )] * 4),
    # === MATH AND NATURAL SCIENCE ===
    Requirement(courses=['MATH-104']),
    Requirement(courses=['MATH-114']),
    Requirement(courses=['CIS-160']),
    Requirement(courses=['CIS-261', 'ESE-301', 'ENM-321', 'STAT-430']),
    Requirement(courses=['MATH-240', 'MATH-312', 'MATH-313', 'MATH-314']),
    Requirement(courses=['PHYS-150', 'PHYS-170', 'MEAM-110']),
    Requirement(courses=['PHYS-151', 'PHYS-171', 'ESE-112']),
    Requirement(categories=['MATH@SEAS', 'NATSCI@SEAS']),
    # # === TODO: TECHNICAL ELECTIVES ===
    *([Requirement(categories=['ENG@SEAS'])] * 6),
    # # # === GENERAL ELECTIVES ===
    Requirement(courses=['EAS-203']),
    *([Requirement(categories=['SS@SEAS', 'H@SEAS'])] * 4),
    *([Requirement(categories=['SS@SEAS', 'H@SEAS', 'TBS@SEAS'])] * 2),
    # # # === TODO: FREE ELECTIVE ===
    Requirement(depts=['FREE'], nickname='Free Elective'),
    Requirement(depts=['FREE'], nickname='Free Elective'),
    Requirement(depts=['FREE'], nickname='Free Elective'),
]
SEAS_DEPTH: RequirementBlock = [
    # TODO need a way to require two from same dept...
]
SEAS_WRIT: RequirementBlock = [
    Requirement(depts=['WRIT'], max_number=99)
]
CIS_MSE: RequirementBlock = [
    # === CORE COURSES ===
    # theory course
    Requirement(courses=['CIS-502', 'CIS-511', 'CIS-677'], nickname='Theory'),
    # systems course or 501
    Requirement(
        courses=['CIS-501', 'CIS-505', 'CIS-548', 'CIS-553', 'CIS-555'],
        nickname='Systems'
    ),
    # core course that can be ML
    Requirement(courses=[
        'CIS-502', 'CIS-511',
        'CIS-505', 'CIS-548', 'CIS-553', 'CIS-555',
        'CIS-520', 'CIS-519', 'CIS-521',
        'CIS-500', 'CIS-501',
    ], nickname='Core'),
    # core course that can't be ML
    Requirement(courses=[
        'CIS-502', 'CIS-511',
        'CIS-505', 'CIS-548', 'CIS-553', 'CIS-555',
        'CIS-500', 'CIS-501',
    ], nickname='Core'),
    # === CIS ELECTIVES ===
    *([Requirement(
        depts=['CIS'], min_number=500, max_number=699,
        nickname='Grad CIS'
    )] * 2),
    Requirement(depts=['CIS'], min_number=500, max_number=700),
    # === CIS OR NON-CIS ELECTIVES ===
    # TODO: revisit this after allowing OR of requirements
    *([Requirement(
        categories=['ENG@SEAS'], min_number=500, max_number=699,
        nickname='Grad Non-CIS'
    )] * 3),
]

ALL_REQUIREMENT_BLOCKS: list[RequirementBlock] = [
    CIS_BSE,
    CIS_MSE,
    SEAS_WRIT,
]
block_idx = lambda block: {tuple(block): b for b, block in enumerate(ALL_REQUIREMENT_BLOCKS)}[tuple(block)]
MAX_DOUBLE_COUNTING: dict[tuple[Index, Index], Optional[int]] = {
    (block_idx(CIS_BSE), block_idx(CIS_MSE)): 3,
    (block_idx(CIS_BSE), block_idx(SEAS_WRIT)): None,
    (block_idx(CIS_MSE), block_idx(SEAS_WRIT)): 0
}

COURSE_REQUESTS: list[CourseRequest] = [
    CourseRequest('CIS-110', 0),
    CourseRequest('MATH-104', 0),
    CourseRequest('BIOL-101', 0),
    CourseRequest('CIS-160', 1),
    CourseRequest('CIS-120', 1),
    CourseRequest('MATH-114', 1),
    CourseRequest('CIS-121', 2),
    CourseRequest('CIS-320', 4),
    CourseRequest('CIS-400', 7),
    CourseRequest('CIS-401', 8),
]
REQUESTED_COURSE_IDS = set(
    course_id for course_id, _ in COURSE_REQUESTS
)

def raise_for_missing_courses(all_courses: list[CourseInfo], requirements: list[Requirement]) -> None:
    courses_from_reqs = set(
        course_id for req in requirements for course_id in req.courses
    )
    course_ids = set(course['id'] for course in all_courses)
    missing_courses = courses_from_reqs.difference(course_ids)
    assert not missing_courses, f'There are missing courses: {missing_courses}'

all_courses = fetch_course_infos()

# add 3 free elective wild character courses (since each course can only be taken once)
for i in range(1, 4):
    all_courses.append({
        "id": f'FREE-{i}',
        "title": "Free Elective 1",
        "semester": "2022C",
        "prerequisites": [],
        "course_quality": None,
        "instructor_quality": None,
        "difficulty": None,
        "work_required": None,
        "crosslistings": [],
        "requirements": [],
        "sections": []
    })

# optimization to make the model smaller:
# only need to consider courses that satisfy at least one of our requirements
# TODO: may also need courses that are prerequisites for courses that satisfy 
all_courses = [
    course for course in all_courses
    if course['id'] in REQUESTED_COURSE_IDS or any(
        req.satisfied_by_course(course)
        for major in ALL_REQUIREMENT_BLOCKS
        for req in major
    )
]

raise_for_missing_courses(all_courses, [req for major in ALL_REQUIREMENT_BLOCKS for req in major])

params = ScheduleParams(
    NUM_SEMESTERS,
    MAX_COURSES_PER_SEMESTER,
    ALL_REQUIREMENT_BLOCKS,
    MAX_DOUBLE_COUNTING
)
generate_schedule(all_courses, COURSE_REQUESTS, params, verbose=True)