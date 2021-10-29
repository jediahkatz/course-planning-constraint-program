# Idea: schedule generator, works like color palette generator (coolors.co)
# Later can expand to 4yr plan

from typing import Callable, Optional
import requests
import os.path
import json
from ortools.sat.python import cp_model
from multiprocessing import Pool

DeptId = str
CourseId = str
ReqCategoryId = str

NUM_SEMESTERS = 8
MAX_COURSES_PER_SEMESTER = 5

COURSES_CACHE_FILE = 'all_courses.json'
COURSE_INFOS_CACHE_FILE = 'course_infos.json'
BASE_URL = 'https://penncourseplan.com/api/base'
LIST_COURSES_API_URL = f'{BASE_URL}/current/courses/'
REQS_API_URL = f'{BASE_URL}/current/requirements/'
GET_COURSE_API = f'{BASE_URL}/current/courses/{{}}/'

class Requirement:
    """
    A requirement that must be satisfied. Contains several optional
    parameters; ALL set parameters must be satisfied for a course to
    satisfy this requirement. If a list parameter is empty, it is
    considered unset.

    The parameters are as follows:

    `categories`: a list of requirement categories; a course must
    fulfill at least one of them.

    `depts`: a list of departments; a course must be part of one of them.

    `courses`: a list of courses; only these courses can satisfy this
    requirement.

    `min_number`: a lower bound for the course number.

    `max_number`: an upper bound for the course number.
    """
    categories: set[ReqCategoryId]
    depts: set[DeptId]
    courses: set[CourseId]
    min_number: int
    max_number: int

    def __init__(
        self, 
        categories: list[ReqCategoryId] = [], 
        depts: list[DeptId] = [],
        courses: list[CourseId] = [],
        min_number = 0,
        max_number = 0,
    ):
        if not (categories or depts or courses):
            raise ValueError('Requirement cannot be empty!')
        self.categories = set(categories)
        self.depts = set(depts)
        self.courses = set(courses)
        self.min_number = min_number
        self.max_number = max_number

    def __str__(self):
        or_strings = [
            f'[{" | ".join(alternatives)}]'
            for alternatives in [self.categories, self.depts, self.courses]
            if alternatives 
        ]
        req_string = ' & '.join(or_strings)
        return f'REQ({req_string})'

    def satisfied_by_course(self, course_info: dict) -> bool:
        categories = set(req['id'] for req in course_info['requirements'])
        course_id = course_info['id']
        dept, number = course_id.split('-')
        try:
            number = int(number)
        except:
            number = 0

        category_satisfied = not self.categories or not categories.isdisjoint(self.categories)
        dept_satisfied = not self.depts or dept in self.depts
        course_satisfied = not self.courses or course_id in self.courses
        min_satisfied = not self.min_number or number >= self.min_number
        max_satisfied = not self.max_number or number <= self.max_number
        return all((
            category_satisfied, dept_satisfied, course_satisfied, min_satisfied, max_satisfied
        ))

CIS_BSE_REQUIREMENTS: list[Requirement] = [
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
        max_number=699
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
    Requirement(categories=['H@SEAS']),
]
CIS_MSE_REQUIREMENTS: list[Requirement] = [
    # === CORE COURSES ===
    # theory course
    Requirement(courses=['CIS-502', 'CIS-511', 'CIS-677']),
    # systems course or 501
    Requirement(courses=['CIS-501', 'CIS-505', 'CIS-548', 'CIS-553', 'CIS-555']),
    # core course that can be ML
    Requirement(courses=[
        'CIS-502', 'CIS-511',
        'CIS-505', 'CIS-548', 'CIS-553', 'CIS-555',
        'CIS-520', 'CIS-519', 'CIS-521',
        'CIS-500', 'CIS-501',
    ]),
    # core course that can't be ML
    Requirement(courses=[
        'CIS-502', 'CIS-511',
        'CIS-505', 'CIS-548', 'CIS-553', 'CIS-555',
        'CIS-500', 'CIS-501',
    ]),
    # === CIS ELECTIVES ===
    *([Requirement(depts=['CIS'], min_number=500, max_number=699)] * 2),
    Requirement(depts=['CIS'], min_number=500, max_number=700),
    # === CIS OR NON-CIS ELECTIVES ===
    # TODO: revisit this after allowing OR of requirements
    *([Requirement(categories=['ENG@SEAS'], min_number=500, max_number=699)] * 3),
]
SEAS_REQUIREMENTS: list[Requirement] = [
    Requirement(categories=['ENG@SEAS']), 
    Requirement(categories=['MATH@SEAS']), 
    Requirement(categories=['H@SEAS']), 
    Requirement(categories=['SS@SEAS']),
    Requirement(depts=['CIS']), 
]
WH_REQUIREMENTS: list[Requirement] = [
    Requirement(categories=['TIA@WH']), 
    Requirement(categories=['GEBS@WH']), 
    Requirement(categories=['H@WH']), 
    Requirement(categories=['SS@WH']), 
    Requirement(categories=['URE@WH']), 
    Requirement(categories=['NSME@WH']),
]
ALL_MAJOR_REQUIREMENTS: list[list[Requirement]] = [
    CIS_BSE_REQUIREMENTS,
    # CIS_MSE_REQUIREMENTS
]

def get_cached_value(filename: str, compute_value: Callable[[], str]):
    # TODO: add expiration
    if os.path.exists(filename):
        print('Cache hit!')
        with open(filename, 'r') as f:
            return json.loads(f.read())

    print('Cache miss!')
    val = compute_value()
    if val is not None:
        with open(filename, 'x') as f:
            f.write(json.dumps(val))
            return val

def fetch_course_info(params) -> Optional[dict]:
    i, course_id, n_total_courses = params
    if i % 50 == 0:
        print(f'Fetching info for course {i}/{n_total_courses}')
    try:
        course_info = json.loads(requests.get(GET_COURSE_API.format(course_id)).text)
        # We don't need this attribute and it takes up lots of space
        del course_info['description']
        return course_info
    except:
        print(f'Failed to fetch info for course {course_id}')
    return None

def compute_course_infos(all_courses):
    course_ids_and_idx = [(i, course['id'], len(all_courses)) for i, course in enumerate(all_courses)]
    with open(COURSES_CACHE_FILE, 'x') as f:
        f.write('[')
        with Pool(20) as p:
            course_infos = p.imap_unordered(fetch_course_info, course_ids_and_idx, 1)
            i = 0
            for course_info in course_infos:
                i += 1
                f.write(
                    json.dumps(course_info) 
                    + (', ' if i <= len(all_courses) else '')
                )
        f.write(']')

    return None

def raise_for_missing_courses(all_courses: list[dict], requirements: list[Requirement]):
    courses_from_reqs = set(
        course_id for req in requirements for course_id in req.courses
    )
    course_ids = set(course['id'] for course in all_courses)
    missing_courses = courses_from_reqs.difference(course_ids)
    assert not missing_courses, f'There are missing courses: {missing_courses}'

# TODO: deduplicate the entries
print('Fetching all course requirement categories')
course_infos: list[dict] = get_cached_value(
    COURSE_INFOS_CACHE_FILE,
    lambda: compute_course_infos(
        get_cached_value(
            COURSES_CACHE_FILE, 
            lambda: json.loads(requests.get(LIST_COURSES_API_URL).text)
        )
    )
)

# optimization to make the model smaller:
# only need to consider courses that satisfy at least one of our requirements
# TODO: add a course that represents a free elective
all_courses = [
    course for course in course_infos 
    if any(
        req.satisfied_by_course(course)
        for major in ALL_MAJOR_REQUIREMENTS
        for req in major
    )
]
course_id_to_index = {
    course['id']: c for c, course in enumerate(all_courses)
}

raise_for_missing_courses(all_courses, [req for major in ALL_MAJOR_REQUIREMENTS for req in major])

print('Constructing model...')
model = cp_model.CpModel()

# takes_course_in_sem[c, s] is true iff we take c in semester s
takes_course_in_sem = {
    (c, s): model.NewBoolVar('') 
    for c in range(len(all_courses)) 
    for s in range(NUM_SEMESTERS+1) 
}
# takes_course_in_sem[c] is true iff we take c in any semester
takes_course = {
    c: model.NewBoolVar('') 
    for c in range(len(all_courses)) 
}
# satisfies[c, m, i] is true iff course c satisfies requirements[i] for major m
satisfies = {
    (c, m, i): model.NewBoolVar('')
    for c in range(len(all_courses))
    for m in range(len(ALL_MAJOR_REQUIREMENTS))
    for i in range(len(ALL_MAJOR_REQUIREMENTS[m]))
}
# satisfies[m, i] is true if requirements[i] for major m is satisfied
is_satisfied = {
    (m, i): model.NewBoolVar('')
    for m in range(len(ALL_MAJOR_REQUIREMENTS))
    for i in range(len(ALL_MAJOR_REQUIREMENTS[m]))
}

# Reify takes_course in terms of takes_course_in_sem
for c in range(len(all_courses)):
    model.AddBoolOr([
        takes_course_in_sem[c, s] for s in range(NUM_SEMESTERS+1)
    ]).OnlyEnforceIf(
        takes_course[c]
    )
    model.AddBoolAnd([
        takes_course_in_sem[c, s].Not() for s in range(NUM_SEMESTERS+1)
    ]).OnlyEnforceIf(
        takes_course[c].Not()
    )

# Limit the number of courses we take per semester
for s in range(1, NUM_SEMESTERS+1):
    model.Add(
        sum(takes_course_in_sem[c, s] for c in range(len(all_courses))) 
        <= 
        MAX_COURSES_PER_SEMESTER
    )

# We only take a course at most once
for c in range(len(all_courses)):
    model.Add(
        sum(takes_course_in_sem[c, s] for s in range(NUM_SEMESTERS)) <= 1
    )

# If we do not take a course, then it does not satisfy anything
for c in range(len(all_courses)):
    for m in range(len(ALL_MAJOR_REQUIREMENTS)):
        for i in range(len(ALL_MAJOR_REQUIREMENTS[m])):
            model.AddImplication(takes_course[c].Not(), satisfies[c, m, i].Not())

# A course cannot satisfy anything that it is not allowed to
for c, course in enumerate(all_courses):
    course_id = course['id']
    for m in range(len(ALL_MAJOR_REQUIREMENTS)):
        for i, req in enumerate(ALL_MAJOR_REQUIREMENTS[m]):
            if not req.satisfied_by_course(course):
                model.Add(satisfies[c, m, i] == 0)

# A course can satisfy at most one requirement per major
for c in range(len(all_courses)):
    for m in range(len(ALL_MAJOR_REQUIREMENTS)):
        model.Add(
            sum(satisfies[c, m, i] for i in range(len(ALL_MAJOR_REQUIREMENTS[m]))) <= 1
        )

# If a course isn't satisfying anything, don't take it
for c in range(len(all_courses)):
    num_satisfied_by_course = model.NewIntVar(0, 1, '')
    model.Add(
        num_satisfied_by_course == sum(
          satisfies[c, m, i] 
          for m in range(len(ALL_MAJOR_REQUIREMENTS))
          for i in range(len(ALL_MAJOR_REQUIREMENTS[m]))
        )
    )
    course_satisfies_something = model.NewBoolVar('')
    model.Add(num_satisfied_by_course == 1).OnlyEnforceIf(course_satisfies_something)
    model.Add(num_satisfied_by_course == 0).OnlyEnforceIf(course_satisfies_something.Not())
    model.AddImplication(course_satisfies_something.Not(), takes_course[c].Not())

# Redundant: a requirement should be satisfied by at exactly one course
for m in range(len(ALL_MAJOR_REQUIREMENTS)):
    for i in range(len(ALL_MAJOR_REQUIREMENTS[m])):
        model.Add(
            sum(satisfies[c, m, i] for c in range(len(all_courses))) == 1
        )

# Reify is_satisfied in terms of satisfies
for m in range(len(ALL_MAJOR_REQUIREMENTS)):
    for i in range(len(ALL_MAJOR_REQUIREMENTS[m])):
        model.AddBoolOr([
            satisfies[c, m, i] for c in range(len(all_courses))
        ]).OnlyEnforceIf(
            is_satisfied[m, i]
        )
        
        model.AddBoolAnd([
            satisfies[c, m, i].Not() for c in range(len(all_courses))
        ]).OnlyEnforceIf(
            is_satisfied[m, i].Not()
        )

        # All requirements must be satisfied
        model.Add(
            is_satisfied[m, i] == 1
        )

WANT_TO_TAKE = [
    ('CIS-110', 0),
    ('MATH-104', 0),
    ('CIS-160', 1),
    ('CIS-120', 1),
    ('MATH-114', 1),
    ('CIS-121', 2),
    ('CIS-240', 3),
    ('CIS-320', 4),
    ('CIS-400', 7),
    ('CIS-401', 8),
]
pre_college_credits = set(
    course_id for course_id, sem in WANT_TO_TAKE if sem == 0
)

for course_id, sem in WANT_TO_TAKE:
    model.Add(
        takes_course_in_sem[course_id_to_index[course_id], sem] == 1
    )

# The zeroth semester represents AP credits, etc and can only be
# populated manually
for c, course in enumerate(all_courses):
    if course['id'] not in pre_college_credits:
        model.Add(
            takes_course_in_sem[c, 0] == 0
        )


num_courses_taken = sum(takes_course[c] for c in range(len(all_courses)))
# model.Add(num_courses_taken == 7)
# model.Minimize(num_courses_taken)

solver = cp_model.CpSolver()
solver.parameters.num_search_workers = 8

print('Solving...')
if solver.Solve(model) in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
    print(f'Solution found ({solver.Value(num_courses_taken)} courses over {NUM_SEMESTERS} semesters)')
    print()
    for s in range(NUM_SEMESTERS+1):
        course_indices = [
            c for c in range(len(all_courses))
            if solver.Value(takes_course_in_sem[c, s]) == 1
        ]
        course_indices_to_major_requirement_indices = {
            c: [
                (m, i)
                for m in range(len(ALL_MAJOR_REQUIREMENTS))
                for i in range(len(ALL_MAJOR_REQUIREMENTS[m]))
                if solver.Value(satisfies[c, m, i]) == 1
            ]
            for c in course_indices
        }

        print(f'SEMESTER {s}:')
        print('------------------')

        for c in course_indices:
            course_id = all_courses[c]['id']
            requirement_names = ', '.join([
                str(ALL_MAJOR_REQUIREMENTS[m][i])
                for (m, i) in course_indices_to_major_requirement_indices[c]
            ])
            print(f'{course_id} (satisfies {requirement_names})')
        
        print()
else:
    print('Not possible to generate a schedule that meets the specifications!\n')

print(solver.ResponseStats())