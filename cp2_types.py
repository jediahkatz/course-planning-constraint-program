from typing import Optional, TypedDict, NamedTuple
from ortools.sat.python.cp_model import IntVar

Id = str
Index = int
VarMap1D = dict[Index, IntVar]
VarMap2D = dict[tuple[Index, Index], IntVar]
VarMap3D = dict[tuple[Index, Index, Index], IntVar]

class CourseRequest(NamedTuple):
    course_id: Id
    semester: Index

class ReqCategoryInfo(TypedDict):
    id: Id
    code: str
    school: str
    semester: str
    name: str

class CourseInfo(TypedDict):
    id: Id
    title: str
    semester: str
    prerequisites: list[Id]
    course_quality: Optional[float]
    instructor_quality: Optional[float]
    difficulty: Optional[float]
    work_required: Optional[float]
    crosslistings: list[str]
    requirements: list[ReqCategoryInfo]
    sections: list[dict]


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
    categories: set[Id]
    depts: set[Id]
    courses: set[Id]
    min_number: int
    max_number: int
    nickname: str

    def __init__(
        self, 
        categories: list[Id] = [], 
        depts: list[Id] = [],
        courses: list[Id] = [],
        min_number = 0,
        max_number = 0,
        nickname = ''
    ):
        if not (categories or depts or courses):
            raise ValueError('Requirement cannot be empty!')
        self.categories = set(categories)
        self.depts = set(depts)
        self.courses = set(courses)
        self.min_number = min_number
        self.max_number = max_number
        self.nickname = nickname

    def __str__(self) -> str:
        if self.nickname:
            return f'<{self.nickname}>'
        or_strings = [
            f'[{" | ".join(alternatives)}]'
            for alternatives in [self.categories, self.depts, self.courses]
            if alternatives 
        ]
        req_string = ' & '.join(or_strings)
        return f'<{req_string}>'

    def satisfied_by_course(self, course_info: CourseInfo) -> bool:
        categories = set(req['id'] for req in course_info['requirements'])
        course_id = course_info['id']
        dept, number_str = course_id.split('-')
        try:
            number = int(number_str)
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
        

RequirementBlock = list[Requirement]

class ScheduleParams(NamedTuple):
    num_semesters: int
    max_courses_per_semester: int
    requirement_blocks: list[RequirementBlock]
    # max_double_counts[block1_index, block2_index] is the max number of courses that can double count for
    # block1 and block2, where block1_idx < block_idx. 'None' entries can double count unlimited times.
    max_double_counts: dict[tuple[Index, Index], Optional[int]]

# SemesterSchedule is a list of course ids, and Schedule is a list of SemesterSchedules
SemesterSchedule = list[Id]
Schedule = list[SemesterSchedule]