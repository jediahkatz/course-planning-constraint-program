from collections import defaultdict
from typing import Optional, Callable, cast
from cp2_types import CourseInfo, Semester, Id
from multiprocessing import Pool
import requests
import os.path
import json

COURSES_CACHE_FILE = 'data/all_courses.json'
COURSE_INFOS_CACHE_FILE = 'data/course_infos.json'
COURSE_OFFER_RATES_CACHE_FILE = 'data/offer_rates.json'
COURSE_HISTORICAL_CREDITS_CACHE_FILE = 'data/historical_credits.json'
BASE_URL = 'https://penncourseplan.com/api/base'
LIST_COURSES_API_URL = f'{BASE_URL}/{{}}/courses/'
REQS_API_URL = f'{BASE_URL}/current/requirements/'
GET_COURSE_API = f'{BASE_URL}/current/courses/{{}}/'

def get_cached_value(filename: str, compute_value: Callable[[], dict]):
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

def get_top_level_operator(prereq_string: str) -> str:
    """ 
    Pre-req parser helper
    Returns AND, OR, MIXED, or NONE as the top lvl operator of a prereq string 
    """
    current_top_level = "NONE"
    open_bracket_count = 0
    parts = prereq_string.upper().split(' ')
    for part in parts:
        if part == '(':
            open_bracket_count += 1
        elif part == ')':
            open_bracket_count -= 1
        elif part in ['AND', 'OR']:
            if open_bracket_count == 0:
                if part != current_top_level and current_top_level != "NONE":
                    current_top_level = "MIXED"
                    break
                current_top_level = part
    return current_top_level

def get_individual_prereq(prereq_string: str) -> Optional[list[str]]:
    """ 
    Pre-req parser helper
    Returns 'DEPT 123' -> [DEPT-123] and '(DEPT 123 OR DEPT 456)' -> [DEPT-123, DEPT-456]
    """
    if 'AND' in prereq_string:
        # 3-level operator not supported
        return None
    prereq_string = prereq_string.replace('(', '').replace(')', '')
    individual_prereq = []
    parts = prereq_string.split(' OR ')
    for part in parts:
        dept_code = part.split(' ')
        if len(dept_code) != 2:
            # Ill-formatted
            return None
        individual_prereq.append(f'{dept_code[0]}-{dept_code[1]}')
    return individual_prereq

def parse_prerequisites(all_courses: list[dict]) -> list[CourseInfo]:
    """ 
    Pre-req parser
    Course prereqs set as an 2D-array: [[Dept-123, Dept-456], [Dept-789]]
    interpreted as: (Dept-123 OR Dept-456) AND Dept-789               
    """
    for course in all_courses:
        prereqs_string: str = course['prerequisites']
        top_level_operator = get_top_level_operator(prereqs_string)
        
        if top_level_operator == "NONE":
            # Expecting format: Dept 123, 456, 789
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
            
            course['prerequisites'] = [[f'{dept}-{code}'] for code in codes]
        
        elif top_level_operator == "MIXED":
            ## Ill-formatted
            course['prerequisites'] = []
            continue
        
        else:
            # Expecting AND of ORs: (DEPT 123 OR DEPT 456) AND DEPT 789
            new_prereq_list = []
            list_of_and_prereqs = prereqs_string.split(' AND ')
            for prereq in list_of_and_prereqs:
                individual_prereq = get_individual_prereq(prereq)
                if individual_prereq is None:
                    # Ill-formatted
                    course['prerequisites'] = []
                    continue
                new_prereq_list.append(individual_prereq)
            course['prerequisites'] = new_prereq_list
    
    return cast(list[CourseInfo], all_courses)

def historical_offered_rate(curr_sem: str) -> dict[Id, dict[str, float]]:
    """
    Look over the last 5 years to guess at which season each
    course is offered in. Return the fraction of semesters
    of each season that each course was offered.
    """
    print('Fetching historical data to see which semester courses are offered')
    HORIZON_YEARS = 5
    curr_year, curr_season = int(curr_sem[:4]), curr_sem[4]
    num_semesters: dict[str, int] = defaultdict(int)
    course_seasons_rates: dict[Id, dict[str, float]] = defaultdict(
        lambda: {season.value: 0 for season in Semester}
    )
    
    for year in range(curr_year, curr_year - HORIZON_YEARS, -1):
        for season in Semester:
            if year == curr_year and season > curr_season:
                continue

            LIST_SEM_COURSES_API_URL = LIST_COURSES_API_URL.format(
                f'{year}{season.value}'
            )
            print(LIST_SEM_COURSES_API_URL)
            num_semesters[season.value] += 1
            courses_offered = set(
                course['id'] for course in 
                json.loads(
                    requests.get(LIST_SEM_COURSES_API_URL).text
                )
            )
            for course_id in courses_offered:
                course_seasons_rates[course_id][season.value] += 1.0

    for course_id, seasons_rates in course_seasons_rates.items():
        for season_str in seasons_rates:
            seasons_rates[season_str] /= num_semesters[season_str]

    return course_seasons_rates


def get_credits_from_old_sections(course_id, curr_sem) -> float:
    """
    For courses missing the `'sections'` key, try to look back at old
    semesters for that data and scrape the number of credits.
    """
    print('Trying to get historical credits data for', course_id)
    HORIZON_YEARS = 5
    curr_year, curr_season = int(curr_sem[:4]), curr_sem[4]    
    for year in range(curr_year, curr_year - HORIZON_YEARS, -1):
        for season in Semester:
            if year == curr_year and season > curr_season:
                continue

            res = requests.get(GET_COURSE_API.format(course_id))
            if res.status_code == 200:
                old_course = json.loads(res.text)
                
                if credits := next((
                        cu for section in old_course.get('sections', []) 
                        if (cu := section['credits']) > 0
                    ), 
                    0
                ):
                    return credits
    return 0
                

# TODO: deduplicate the entries
def fetch_course_data() -> list[CourseInfo]:
    """ Fetch a list of each course's information from the PennCourses API. """
    print('Fetching all courses\' requirement categories')
    LIST_CURRENT_SEM_COURSES_API_URL = LIST_COURSES_API_URL.format('current')
    course_infos: list[dict] = get_cached_value(
        COURSE_INFOS_CACHE_FILE,
        lambda: compute_course_infos(
            get_cached_value(
                COURSES_CACHE_FILE, 
                lambda: json.loads(
                    requests.get(LIST_CURRENT_SEM_COURSES_API_URL).text
                )
            )
        )
    )
    curr_sem = course_infos[0]['semester']
    course_seasons_rates = get_cached_value(
        COURSE_OFFER_RATES_CACHE_FILE,
        lambda: historical_offered_rate(curr_sem)
    )
    course_historical_credits = get_cached_value(
        COURSE_HISTORICAL_CREDITS_CACHE_FILE, 
        lambda: {
            course['id']: get_credits_from_old_sections(course['id'], curr_sem)
            for course in course_infos
            if 'credits' not in course 
            and not course.get('sections')
            # TODO: lots of courses with no data, haven't been taught lately...
            # will have to figure out how to handle them
            and course['title']
        }
    )
    for course in course_infos:
        course['rate_offered'] = course_seasons_rates.get(
            course['id'], {season.value: 0 for season in Semester}
        )
        # assuming CU aren't split between e.g. lecture and lab (but I think that's true)
        if 'credits' not in course:
            if course['title'] and not course.get('sections'):
                course['credits'] = course_historical_credits[course['id']]
                course['sections'] = []
            else:
                course['credits'] = next((
                        cu for section in course.get('sections', []) 
                        if (cu := section['credits']) > 0
                    ),
                    0.0
                )

    return parse_prerequisites(course_infos)