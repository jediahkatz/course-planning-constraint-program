from typing import Optional, Callable, cast
from cp2_types import CourseInfo
from multiprocessing import Pool
import requests
import os.path
import json

COURSES_CACHE_FILE = 'all_courses.json'
COURSE_INFOS_CACHE_FILE = 'course_infos.json'
BASE_URL = 'https://penncourseplan.com/api/base'
LIST_COURSES_API_URL = f'{BASE_URL}/current/courses/'
REQS_API_URL = f'{BASE_URL}/current/requirements/'
GET_COURSE_API = f'{BASE_URL}/current/courses/{{}}/'

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

def fetch_course_info(params) -> Optional[CourseInfo]:
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
                if course_info is not None:
                    f.write(
                        json.dumps(course_info) 
                        + (', ' if i <= len(all_courses) else '')
                    )
        f.write(']')

    return None

# right now we only handle of the form 'DEPT 123, 456'
def parse_prerequisites(all_courses: list[dict]) -> list[CourseInfo]:
    for course in all_courses:
        prereqs_string: str = course['prerequisites']
        parts = prereqs_string.split(', ')
        first_course = parts[0].split(' ')
        if len(first_course) != 2:
            # Ill-formatted
            course['prerequisites'] = []
            continue
        dept, code = first_course
        codes = [code] + parts[1:]
        if dept != dept.strip() or any(code != code.strip() for code in codes):
            # Ill-formatted
            course['prerequisites'] = []
            continue
            
        course['prerequisites'] = [f'{dept}-{code}' for code in codes]
    
    return cast(list[CourseInfo], all_courses)

# TODO: deduplicate the entries
def fetch_course_infos() -> list[CourseInfo]:
    """ Fetch a list of each course's information from the PennCourses API. """
    print('Fetching all courses\' requirement categories')
    course_infos: list[dict] = get_cached_value(
        COURSE_INFOS_CACHE_FILE,
        lambda: compute_course_infos(
            get_cached_value(
                COURSES_CACHE_FILE, 
                lambda: json.loads(requests.get(LIST_COURSES_API_URL).text)
            )
        )
    )

    return parse_prerequisites(course_infos)
