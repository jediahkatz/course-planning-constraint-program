from typing import List, Optional, Type, TypedDict, NamedTuple, Tuple
from ortools.sat.python.cp_model import IntVar
from enum import Enum

from setuptools import Require

Id = str
Uid = int
Index = int
BoolVar = Type[IntVar]

class CourseRequest(NamedTuple):
    course_id: Id
    semester: Optional[Index]

class CompletedCourse(NamedTuple):
    course_id: Id
    semester: Index
    satisfies: list[Uid]

class ReqCategoryInfo(TypedDict):
    id: Id
    code: str
    school: str
    semester: str
    name: str

class Semester(Enum):
    SPRING = 'A'
    SUMMER = 'B'
    FALL = 'C'

    def __gt__(self, other):
        if isinstance(other, str):
            return self.value > other
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented
    
class CourseInfo(TypedDict):
    id: Id
    title: str
    semester: str
    rate_offered: dict[str, float]
    prerequisites: list[list[Id]]
    course_quality: Optional[float]
    instructor_quality: Optional[float]
    difficulty: Optional[float]
    work_required: Optional[float]
    crosslistings: list[str]
    requirements: list[ReqCategoryInfo]
    sections: list[dict]
    credits: float

class BaseRequirement:
    """
    A requirement that must be satisfied. Contains several optional
    parameters; ALL set parameters must be satisfied for a course to
    satisfy this requirement. If a list parameter is empty, it is
    considered unset.

    Parameters:

    `categories`: a list of requirement categories; a course must
    fulfill at least one of them.

    `depts`: a list of departments; a course must be part of one of them.

    `courses`: a list of courses; only these courses can satisfy this
    requirement.

    `min_number`: a lower bound for the course number.

    `max_number`: an upper bound for the course number.

    `allow_partial_cu`: whether this can be satisfied with 0.5cu + 0.5cu.
    """
    uid: Uid = 0

    def __init__(
        self,
        categories: list[Id] = [], 
        depts: list[Id] = [],
        courses: list[Id] = [],
        min_number: int = 0,
        max_number: int = 0,
        allow_partial_cu: bool = False,
        nickname: str = ''
    ):
        assert categories or depts or courses, 'Empty requirement!'

        self.categories = set(categories)
        self.depts = set(depts)
        self.courses = set(courses)
        self.min_number = min_number
        self.max_number = max_number
        self.allow_partial_cu = allow_partial_cu    # TODO: unused
        self.nickname = nickname

        self.uid = BaseRequirement.uid
        BaseRequirement.uid += 1

    def __repr__(self) -> str:
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
        if 'FREE' in self.categories:
            return True
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
        
class Requirement:
    """
    Either a single BaseRequirement, or a set of Requirements
    such that at least k must be satisfied. We can also specify
    a minimum number of CUs that must be counted towards the
    subrequirements.
    """
    uid: Uid = 0

    def __init__(
        self,
        base_requirement: Optional[BaseRequirement] = None, 
        multi_requirements = None,
        min_satisfied_reqs: int = 1,
        min_credits: float = 0,
        nickname: str = ''
    ):
        assert not (multi_requirements and base_requirement), 'Can\'t have both base and multi requirements!'
        assert min_satisfied_reqs > 0 or min_credits > 0, 'Vacuous requirement!'
        assert min_credits % 1 in [0, 0.5, 1], 'Requirements of *.25 credits not supported!'

        self.is_multi_requirement = (base_requirement is None)
        self._base_requirement: Optional[BaseRequirement] = base_requirement
        self.multi_requirements: list[Requirement] = (multi_requirements or [])
        self.min_satisfied_reqs = min_satisfied_reqs
        self.min_credits = min_credits
        self.nickname = nickname

        self.uid = Requirement.uid
        Requirement.uid += 1

    def __repr__(self) -> str:
        if self.nickname:
            return f'<{self.nickname}>'

        if self.is_multi_requirement:
            at_least_strs = []
            if self.min_satisfied_reqs > 0:
                at_least_strs.append(str(self.min_satisfied_reqs))
            if self.min_credits > 0:
                at_least_strs.append(f'{self.min_credits}cu')
            return f'>=({" / ".join(at_least_strs)})[{",".join(str(r) for r in self.multi_requirements)}]'
        
        return str(self.base_requirement)

    @property
    def base_requirement(self):
        assert not self.is_multi_requirement, 'Can\'t get base_requirement of a multi requirement!'
        assert self._base_requirement
        return self._base_requirement

    @classmethod
    def base(cls, **kwargs):
        """ Create a new Requirement that wraps a single BaseRequirement. """
        return Requirement(base_requirement=BaseRequirement(**kwargs))

    @classmethod
    def all(cls, sub_requirements: list, nickname=''):
        """ Create a new Requirement that is satisfied if any subrequirement is satisfied. """
        return Requirement(
            nickname=nickname,
            min_satisfied_reqs=len(sub_requirements),
            multi_requirements=sub_requirements
        )
    
    @classmethod
    def any(cls, sub_requirements: list, nickname=''):
        """ Create a new Requirement that is satisfied if all subrequirements are satisfied. """
        return Requirement(
            nickname=nickname,
            min_satisfied_reqs=1,
            multi_requirements=sub_requirements
        )


RequirementBlock = list[Requirement]

class ScheduleParams(NamedTuple):
    num_semesters: int
    max_credits_per_semester: int
    min_credits_per_semester: int
    requirement_blocks: list[RequirementBlock]
    # max_double_counts[block1_index, block2_index] is the max number of credits that can double count for
    # block1 and block2, where block1_idx < block_idx. 'None' entries can double count unlimited times.
    max_double_counts: dict[tuple[Index, Index], Optional[int]]
    # a list of blocks such that no course can count for three of these blocks at the same time (e.g. majors)
    cannot_triple_count: set[Index]

# SemesterSchedule is a list of course ids, and Schedule is a list of SemesterSchedules
SemesterSchedule = list[Id]
Schedule = list[SemesterSchedule]