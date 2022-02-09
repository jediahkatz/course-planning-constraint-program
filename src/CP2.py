# Idea: schedule generator, works like color palette generator (coolors.co)
# Later can expand to 4yr plan

from collections import defaultdict
from typing import Optional

from cp2_types import CourseRequest, CompletedCourse, Index, CourseInfo, Requirement, RequirementBlock, ScheduleParams
from requirement_blocks import (
    CIS_BAS,
    CIS_BREADTH,
    OLD_CIS_BSE,
    CIS_BSE,
    DSGN_MAJOR, 
    SEAS_WRIT, 
    CIS_MSE,
    MATH_MINOR, 
    STAT_MINOR,
    DATS_MINOR
)
from fetch_data import fetch_course_data
from solver import generate_schedule
# from pdf_parse import convert_to_images, write_output_txt, get_completed_courses

NUM_SEMESTERS = 8
MAX_CREDITS_PER_SEMESTER = 5
MIN_CREDITS_PER_SEMESTER = 0

ALL_REQUIREMENT_BLOCKS: list[RequirementBlock] = [
    # CIS_BSE,
    # CIS_BREADTH,
    CIS_BAS,
    # CIS_MSE,
    # SEAS_WRIT,
    # MATH_MINOR,
    # DATS_MINOR,
    DSGN_MAJOR,
]
block_idx = lambda block: {tuple(block): b for b, block in enumerate(ALL_REQUIREMENT_BLOCKS)}[tuple(block)]
MAX_DOUBLE_COUNTING: dict[tuple[Index, Index], Optional[int]] = defaultdict(lambda: None, {
    # (block_idx(CIS_BSE), block_idx(CIS_MSE)): 3,
    # (block_idx(CIS_BREADTH), block_idx(DSGN_MAJOR)): 0,
})
CANNOT_TRIPLE_COUNT: set[Index] = set([
    # block_idx(CIS_BSE),
    # block_idx(CIS_MSE),
])


COURSE_REQUESTS: list[CourseRequest] = [
    # CourseRequest('CIS-400', 7),
    CourseRequest('DSGN-488', 7),
    # CourseRequest('CIS-401', 8),
    CourseRequest('DSGN-489', 8),
]
REQUESTED_COURSE_IDS = set(
    course_id for course_id, _ in COURSE_REQUESTS
)
completed_courses: list[CompletedCourse] = [
    # pre-college credit
    CompletedCourse('CIS-110', 0, []),
    CompletedCourse('EAS-091', 0, []),
    CompletedCourse('MATH-104', 0, []),
    CompletedCourse('SPAN-202', 0, []),
    CompletedCourse('BIOL-101', 0, []),
    # freshman fall
    CompletedCourse('CIS-120', 1, []),
    CompletedCourse('CIS-160', 1, []),
    CompletedCourse('MATH-114', 1, []),
    CompletedCourse('PHYS-150', 1, []),
    CompletedCourse('HIST-033', 1, []),
    # freshman spring
    CompletedCourse('CIS-121', 2, []),
    CompletedCourse('CIS-262', 2, []),
    CompletedCourse('PHYS-151', 2, []),
    CompletedCourse('WRIT-025', 2, [SEAS_WRIT[0].base_requirement.uid, OLD_CIS_BSE[30].base_requirement.uid]),
    # sophmore fall
    CompletedCourse('CIS-240', 3, []),
    CompletedCourse('NETS-412', 3, []),
    CompletedCourse('CIS-261', 3, []),
    CompletedCourse('CIS-500', 3, []),
    CompletedCourse('MATH-502', 3, []),
    CompletedCourse('MATH-240', 3, []),
    # sophomore spring
    CompletedCourse('CIS-320', 4, []),
    CompletedCourse('CIS-519', 4, [OLD_CIS_BSE[10].multi_requirements[0].base_requirement.uid, CIS_MSE[2].base_requirement.uid, DATS_MINOR[1].base_requirement.uid]),
    CompletedCourse('CIS-545', 4, []),
    CompletedCourse('MATH-514', 4, [OLD_CIS_BSE[18].base_requirement.uid, CIS_MSE[7].base_requirement.uid]),
    CompletedCourse('EAS-203', 4, []),
    # junior fall
    CompletedCourse('CIS-380', 5, []),
    CompletedCourse('CIS-677', 5, []),
    CompletedCourse('CIS-552', 5, []),
    CompletedCourse('CIMS-103', 5, []),
    CompletedCourse('STSC-278', 5, []),
    CompletedCourse('MATH-241', 5, []),
    # # junior spring
    CompletedCourse('CIS-341', 6, []),
    CompletedCourse('CIS-471', 6, []),
    CompletedCourse('CIS-559', 6, [OLD_CIS_BSE[12].multi_requirements[0].base_requirement.uid, CIS_MSE[5].base_requirement.uid]),
    CompletedCourse('PHIL-414', 6, []),
    CompletedCourse('FNAR-340', 6, []),
    # senior fall
    CompletedCourse('CIS-505', 7, []),
    CompletedCourse('CIS-547', 7, []),
    CompletedCourse('CIS-400', 7, []),
    CompletedCourse('FNAR-342', 7, []),
    CompletedCourse('MGMT-291', 7, []),
    # senior spring
    CompletedCourse('CIS-401', 8, []),
    CompletedCourse('CIS-195', 8, []),
    CompletedCourse('ESE-190', 8, []),
    CompletedCourse('PSYC-266', 8, []),
    CompletedCourse('STAT-431', 8, []),
    CompletedCourse('CIS-555', 8, []),
    # # CompletedCourse('NETS-150', 8, []),
    # # CompletedCourse('HIST-210', 8, []),
]

# janice
completed_courses = [
    CompletedCourse('CIS-110', 0, []),
    CompletedCourse('MATH-104', 0, []),
    CompletedCourse('PHYS-150', 0, []),
    CompletedCourse('CHEM-101', 0, []),
    CompletedCourse('STAT-430', 0, []),

    CompletedCourse('CIS-120', 1, []),
    CompletedCourse('CIS-160', 1, []),
    CompletedCourse('LING-115', 1, []),
    CompletedCourse('MATH-114', 1, []),
    CompletedCourse('WRIT-088', 1, []),

    CompletedCourse('CIS-121', 2, []),
    CompletedCourse('DSGN-264', 2, []),
    CompletedCourse('MATH-240', 2, []),
    CompletedCourse('NETS-150', 2, []),
    CompletedCourse('PHYS-151', 2, []),

    CompletedCourse('CIS-240', 3, []),
    CompletedCourse('CIS-262', 3, []),
    CompletedCourse('DSGN-234', 3, []),
    CompletedCourse('DSGN-300', 3, []),
    CompletedCourse('DSGN-566', 3, []),
    CompletedCourse('NETS-212', 3, []),

    CompletedCourse('ARTH-102', 4, []),
    CompletedCourse('CIS-320', 4, []),
    CompletedCourse('CIS-450', 4, []),
    CompletedCourse('DSGN-245', 4, []),
    CompletedCourse('EAS-203', 4, []),
    CompletedCourse('VLST-101', 4, []),
]

# cindy
completed_courses = [
    
]

# parse pdf to get completed courses
# SAVE_TO = "./img/"
# PDF_FILE = "Akshit_Sharma_Transcript.pdf"

# total_images = convert_to_images(save_to=SAVE_TO, pdf_file=PDF_FILE)
# outfile = write_output_txt(total_images=total_images, img_file_path=SAVE_TO)
# completed_courses = get_completed_courses(outfile)

all_courses = fetch_course_data()

# assemble list of completed courses and their respective semesters
all_course_ids = set(course_info["id"] for course_info in all_courses)

COMPLETED: list[CompletedCourse] = [
    CompletedCourse(course_id, sem, satisfies) 
    for course_id, sem, satisfies in completed_courses 
    if course_id in all_course_ids
]

COMPLETED_COURSE_IDS = set(
    course_id for course_id, _, _ in COMPLETED
)

REQUESTED_AND_COMPLETED_IDS = COMPLETED_COURSE_IDS.union(REQUESTED_COURSE_IDS)

params = ScheduleParams(
    num_semesters=NUM_SEMESTERS,
    max_credits_per_semester=MAX_CREDITS_PER_SEMESTER,
    min_credits_per_semester=MIN_CREDITS_PER_SEMESTER,
    requirement_blocks=ALL_REQUIREMENT_BLOCKS,
    max_double_counts=MAX_DOUBLE_COUNTING,
    cannot_triple_count=CANNOT_TRIPLE_COUNT,
    total_max_credits=40,
)
generate_schedule(all_courses, COURSE_REQUESTS, COMPLETED, params, verbose=True)