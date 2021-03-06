from collections import defaultdict
from itertools import count
import sched
from typing import Sequence
from cp2_types import CompletedCourse, CourseInfo, CourseRequest, ScheduleParams, Requirement
from solver import generate_schedule
import pytest


def test_empty(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    assert (soln := generate_schedule(sample_courses_info, [], [], params))
    schedule, _ = soln
    assert len(schedule) == 2
    for sem in schedule:
        assert len(sem) == 0


def test_requirement_one_course(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[[
            Requirement.base(courses=['CIS-120'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    assert (soln := generate_schedule(sample_courses_info, [], [], params))
    schedule, _ = soln
    assert len(schedule) == 2
    # No courses should be scheduled in the precollege semester
    assert schedule[0] == []
    assert schedule[1] == ['CIS-120']


def test_requirement_one_category(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[[
            Requirement.base(categories=['MATH@SEAS'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    assert (soln := generate_schedule(sample_courses_info, [], [], params))
    schedule, _ = soln
    assert len(schedule) == 2
    # No courses should be scheduled in the precollege semester
    assert schedule[0] == []
    assert len(schedule[1]) == 1
    course_id = schedule[1][0]
    course_info = next(info for info in sample_courses_info if info['id'] == course_id)
    assert any(req['id'] == 'MATH@SEAS' for req in course_info['requirements'])
    

def test_requirement_one_dept(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[[
            Requirement.base(depts=['CIS'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    assert (soln := generate_schedule(sample_courses_info, [], [], params))
    schedule, _ = soln
    assert len(schedule) == 2
    # No courses should be scheduled in the precollege semester
    assert schedule[0] == []
    assert len(schedule[1]) == 1
    course_id = schedule[1][0]
    assert course_id.startswith('CIS')


def test_requirement_one_course_not_exists(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[[
            Requirement.base(courses=['CIS-420'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    assert not generate_schedule(sample_courses_info, [], [], params)


def test_requirement_one_category_not_exists(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[[
            Requirement.base(categories=['FUN@SEAS'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    assert not generate_schedule(sample_courses_info, [], [], params)


def test_requirement_one_dept_not_exists(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[[
            Requirement.base(depts=['OMG'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    assert not generate_schedule(sample_courses_info, [], [], params)


def test_requirement_same_course_not_allowed(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[[
            Requirement.base(courses=['CIS-120']),
            Requirement.base(courses=['CIS-120'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    assert not generate_schedule(sample_courses_info, [], [], params)


def test_requirement_two_courses(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[[
            Requirement.base(courses=['CIS-120']),
            Requirement.base(courses=['CIS-160'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    assert (soln := generate_schedule(sample_courses_info, [], [], params))
    schedule, _ = soln
    assert len(schedule) == 2
    # No courses should be scheduled in the precollege semester
    assert schedule[0] == []
    assert not (set(schedule[1]) ^ {'CIS-120', 'CIS-160'})


def test_requirement_two_depts_same(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[[
            Requirement.base(depts=['CIS']),
            Requirement.base(depts=['CIS'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    assert (soln := generate_schedule(sample_courses_info, [], [], params))
    schedule, _ = soln
    assert len(schedule) == 2
    # No courses should be scheduled in the precollege semester
    assert schedule[0] == []
    assert len(schedule[1]) == 2
    # Courses should not be the same
    assert len(set(schedule[1])) == 2
    for course in schedule[1]:
        assert course.startswith('CIS')


def test_requirement_two_depts_different(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[[
            Requirement.base(depts=['CIS']),
            Requirement.base(depts=['MATH'])
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    assert (soln := generate_schedule(sample_courses_info, [], [], params))
    schedule, _ = soln
    assert len(schedule) == 2
    # No courses should be scheduled in the precollege semester
    assert schedule[0] == []
    assert len(schedule[1]) == 2
    cis, math = sorted(schedule[1])
    assert cis.startswith('CIS')
    assert math.startswith('MATH')


def test_more_requirements_than_slots(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[[
            Requirement.base(depts=['CIS']),
            Requirement.base(depts=['CIS']),
            Requirement.base(depts=['MATH']),
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    assert not generate_schedule(sample_courses_info, [], [], params)


def test_one_course_request(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    course_requests = [
        CourseRequest('CIS-120', 1)
    ]
    assert (soln := generate_schedule(sample_courses_info, course_requests, [], params))
    schedule, _ = soln
    # No courses should be scheduled in the precollege semester
    assert schedule[0] == []
    assert schedule[1] == ['CIS-120']


def test_two_course_requests(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    course_requests = [
        CourseRequest('CIS-120', 1),
        CourseRequest('CIS-160', 2)
    ]
    assert (soln := generate_schedule(sample_courses_info, course_requests, [], params))
    schedule, _ = soln
    # No courses should be scheduled in the precollege semester
    assert schedule[0] == []
    assert schedule[1] == ['CIS-120']
    assert schedule[2] == ['CIS-160']


def test_one_course_request_any_sem(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    course_requests = [
        CourseRequest('CIS-120', None)
    ]
    assert (soln := generate_schedule(sample_courses_info, course_requests, [], params))
    schedule, _ = soln
    # No courses should be scheduled in the precollege semester
    assert schedule[0] == []
    assert schedule[1] + schedule[2] == ['CIS-120']


def test_two_course_requests_any_sem(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    course_requests = [
        CourseRequest('CIS-120', None),
        CourseRequest('CIS-160', None)
    ]
    assert (soln := generate_schedule(sample_courses_info, course_requests, [], params))
    schedule, _ = soln
    # No courses should be scheduled in the precollege semester
    assert schedule[0] == []
    assert set(schedule[1] + schedule[2]) == {'CIS-120', 'CIS-160'}


def test_invalid_course_request(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    course_requests = [
        CourseRequest('CIS-120', 2)
    ]
    with pytest.raises(KeyError):
        assert not generate_schedule(sample_courses_info, course_requests, [], params)

@pytest.mark.skip('moved to CompletedCourses')
def test_one_course_request_precollege(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    course_requests = [
        CourseRequest('CIS-120', 0)
    ]
    assert (soln := generate_schedule(sample_courses_info, course_requests, [], params))
    schedule, _ = soln
    assert schedule[0] == ['CIS-120']
    assert schedule[1] == []


def test_prerequisites_feasible(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[[
            Requirement.base(courses=['CIS-262']),
            Requirement.base(courses=['CIS-160']),
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )

    assert (soln := generate_schedule(sample_courses_info, [], [], params))
    schedule, _ = soln
    assert schedule[1] == ['CIS-160']
    assert schedule[2] == ['CIS-262']


def test_prerequisites_infeasible(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[[
            Requirement.base(courses=['CIS-121']),
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    assert not generate_schedule(sample_courses_info, [], [], params)


def test_prerequisites_requests_infeasible(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[[
            Requirement.base(courses=['CIS-262']),
        ]],
        # No double counting
        max_double_counts=defaultdict(int),
        cannot_triple_count=set(),
    )
    course_requests = [
        CourseRequest('CIS-262', 1)
    ]
    assert not generate_schedule(sample_courses_info, course_requests, [], params)


def test_double_count(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[
            [math := Requirement.base(categories=['MATH@SEAS'])],
            [fge := Requirement.base(categories=['FGE@WH'])],
        ],
        # Can double count once
        max_double_counts=defaultdict(lambda: 1),
        cannot_triple_count=set(),
    )

    assert (soln := generate_schedule(sample_courses_info, [], [], params))
    schedule, counts_for = soln
    assert schedule[0] == []
    assert len(schedule[1]) == 1
    course_id = schedule[1][0]
    info = next(info for info in sample_courses_info if info['id'] == course_id)
    req_ids = [req['id'] for req in info['requirements']]

    assert 'MATH@SEAS' in req_ids
    assert 'FGE@WH' in req_ids
    assert counts_for[course_id] == [(0, math.base_requirement), (1, fge.base_requirement)]


def test_double_count_infinite_one_semester(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=2,
        requirement_blocks=[
            [
                c120_0 := Requirement.base(courses=['CIS-120']), 
                c160_0 := Requirement.base(courses=['CIS-160'])
            ],
            [
                c160_1 := Requirement.base(courses=['CIS-160']), 
                c120_1 := Requirement.base(courses=['CIS-120'])
            ],
        ],
        # Can double count infinite times
        max_double_counts=defaultdict(lambda: None),
        cannot_triple_count=set(),
    )

    assert (soln := generate_schedule(sample_courses_info, [], [], params))
    schedule, counts_for = soln
    assert schedule[0] == []
    assert not set(schedule[1]) ^ {'CIS-120', 'CIS-160'}
    assert counts_for['CIS-120'] == [(0, c120_0.base_requirement), (1, c120_1.base_requirement)]
    assert counts_for['CIS-160'] == [(0, c160_0.base_requirement), (1, c160_1.base_requirement)]


def test_double_count_infinite_multiple_semesters(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[
            [
                c160_0 := Requirement.base(courses=['CIS-160']), 
                c262_0 := Requirement.base(courses=['CIS-262'])
            ],
            [
                c262_1 := Requirement.base(courses=['CIS-262']), 
                c160_1 := Requirement.base(courses=['CIS-160'])
            ],
        ],
        # Can double count infinite times
        max_double_counts=defaultdict(lambda: None),
        cannot_triple_count=set(),
    )

    assert (soln := generate_schedule(sample_courses_info, [], [], params))
    schedule, counts_for = soln
    assert schedule[0] == []
    assert schedule[1] == ['CIS-160']
    assert schedule[2] == ['CIS-262']
    assert counts_for['CIS-160'] == [(0, c160_0.base_requirement), (1, c160_1.base_requirement)]
    assert counts_for['CIS-262'] == [(0, c262_0.base_requirement), (1, c262_1.base_requirement)]


def test_no_double_count(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[
            [Requirement.base(categories=['MATH@SEAS'])],
            [Requirement.base(categories=['FGE@WH'])],
        ],
        # No double counting
        max_double_counts=defaultdict(lambda: 0),
        cannot_triple_count=set(),
    )

    assert not generate_schedule(sample_courses_info, [], [], params)


def test_no_triple_count(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[
            [Requirement.base(categories=['MATH@SEAS'])],
            [Requirement.base(categories=['FGE@WH'])],
            [Requirement.base(categories=['MFR@SAS'])],
        ],
        # Infinite double counting but we can never triple count
        # using any blocks listed in `cannot_triple_count`
        max_double_counts=defaultdict(lambda: None),
        cannot_triple_count={0, 1, 2},
    )

    assert not generate_schedule(sample_courses_info, [], [], params)


def test_triple_count(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=1,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[
            [math := Requirement.base(categories=['MATH@SEAS'])],
            [fge := Requirement.base(categories=['FGE@WH'])],
            [mfr := Requirement.base(categories=['MFR@SAS'])],
        ],
        # We can triple count here since `cannot_triple_count` is empty
        max_double_counts=defaultdict(lambda: None),
        cannot_triple_count=set(),
    )

    assert (soln := generate_schedule(sample_courses_info, [], [], params, verbose=True))
    schedule, counts_for = soln
    assert schedule[0] == []
    assert schedule[1] == ['MATH-104']
    assert counts_for['MATH-104'] == [(0, math.base_requirement), (1, fge.base_requirement), (2, mfr.base_requirement)]


def test_cant_take_fall_course_in_spring(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[
            [Requirement.base(courses=['CIS-261'])]
        ],
        max_double_counts=defaultdict(lambda: None),
        cannot_triple_count=set(),
    )

    assert not generate_schedule(sample_courses_info, [], [], params)


def test_can_take_fall_course_in_fall(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=3,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[
            [Requirement.base(courses=['CIS-160'])],
            [Requirement.base(courses=['CIS-261'])]
        ],
        max_double_counts=defaultdict(lambda: None),
        cannot_triple_count=set(),
    )

    assert (soln := generate_schedule(sample_courses_info, [], [], params))
    schedule, _ = soln
    print(schedule, _)
    assert schedule[0] == []
    assert schedule[1] + schedule[2] == ['CIS-160']
    assert schedule[3] == ['CIS-261']


def test_multi_course_requirement_any(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[
            [Requirement.any([
                c160 := Requirement.base(courses=['CIS-160']),
                Requirement.base(courses=['CIS-262']),
            ])],
        ],
        max_double_counts=defaultdict(lambda: None),
        cannot_triple_count=set(),
    )

    assert (soln := generate_schedule(sample_courses_info, [], [], params))
    schedule, counts_for = soln
    assert schedule[0] == []
    assert schedule[1] + schedule[2] == ['CIS-160']

    assert counts_for['CIS-160'] == [(0, c160.base_requirement)]


def test_multi_course_requirement_all(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[
            [Requirement.all([
                c160 := Requirement.base(courses=['CIS-160']),
                c262 := Requirement.base(courses=['CIS-262']),
            ])],
        ],
        max_double_counts=defaultdict(lambda: None),
        cannot_triple_count=set(),
    )

    assert (soln := generate_schedule(sample_courses_info, [], [], params))
    schedule, counts_for = soln
    assert schedule[0] == []
    assert schedule[1] == ['CIS-160']
    assert schedule[2] == ['CIS-262']

    assert counts_for['CIS-160'] == [(0, c160.base_requirement)]
    assert counts_for['CIS-262'] == [(0, c262.base_requirement)]


def test_multi_course_requirement_some(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[
            [Requirement(
                min_satisfied_reqs=2,
                multi_requirements=[
                    c160 := Requirement.base(courses=['CIS-160']),
                    Requirement.base(courses=['CIS-320']),
                    c262 := Requirement.base(courses=['CIS-262']),
                ],
            )],
        ],
        max_double_counts=defaultdict(lambda: None),
        cannot_triple_count=set(),
    )

    assert (soln := generate_schedule(sample_courses_info, [], [], params))
    schedule, counts_for = soln
    assert schedule[0] == []
    assert schedule[1] == ['CIS-160']
    assert schedule[2] == ['CIS-262']

    assert counts_for['CIS-160'] == [(0, c160.base_requirement)]
    assert counts_for['CIS-262'] == [(0, c262.base_requirement)]


def test_multi_course_requirement_nested_1(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[
            [Requirement.any([
                Requirement.all([
                    c120 := Requirement.base(courses=['CIS-120']),
                    c240 := Requirement.base(courses=['CIS-240']),
                ]),
                Requirement.all([
                    Requirement.base(courses=['CIS-160']),
                    Requirement.base(courses=['CIS-262']),
                ]),
            ])],
        ],
        max_double_counts=defaultdict(lambda: None),
        cannot_triple_count=set(),
    )
    course_requests = [
        CourseRequest('CIS-120', 1)
    ]

    assert (soln := generate_schedule(sample_courses_info, course_requests, [], params))
    schedule, counts_for = soln
    assert schedule[0] == []
    assert schedule[1] == ['CIS-120']
    assert schedule[2] == ['CIS-240']

    assert counts_for['CIS-120'] == [(0, c120.base_requirement)]
    assert counts_for['CIS-240'] == [(0, c240.base_requirement)]


def test_multi_course_requirement_nested_2(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[
            [Requirement.any([
                Requirement.all([
                    Requirement.base(courses=['CIS-120']),
                    Requirement.base(courses=['CIS-240']),
                ]),
                Requirement.all([
                    c160 := Requirement.base(courses=['CIS-160']),
                    c262 := Requirement.base(courses=['CIS-262']),
                ]),
            ])],
        ],
        max_double_counts=defaultdict(lambda: None),
        cannot_triple_count=set(),
    )
    course_requests = [
        CourseRequest('CIS-160', 1)
    ]

    assert (soln := generate_schedule(sample_courses_info, course_requests, [], params))
    schedule, counts_for = soln
    assert schedule[0] == []
    assert schedule[1] == ['CIS-160']
    assert schedule[2] == ['CIS-262']

    assert counts_for['CIS-160'] == [(0, c160.base_requirement)]
    assert counts_for['CIS-262'] == [(0, c262.base_requirement)]


def test_half_credits_allowed(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=0.5,
        requirement_blocks=[
            [Requirement(
                min_credits=1,
                multi_requirements=[cis := Requirement.base(
                    depts=['CIS'], allow_partial_cu=True
                )]
            )],
        ],
        max_double_counts=defaultdict(lambda: None),
        cannot_triple_count=set(),
    )

    assert (soln := generate_schedule(sample_courses_info, [], [], params))
    schedule, counts_for = soln
    assert schedule[0] == []
    assert set(schedule[1] + schedule[2]) == {'CIS-188', 'CIS-189'}

    assert counts_for['CIS-188'] == [(0, cis.base_requirement)]
    assert counts_for['CIS-189'] == [(0, cis.base_requirement)]


def test_half_credits_not_allowed(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=0.5,
        requirement_blocks=[
            [Requirement(
                min_credits=1,
                multi_requirements=[cis := Requirement.base(depts=['CIS'])]
            )],
        ],
        max_double_counts=defaultdict(lambda: None),
        cannot_triple_count=set(),
    )

    assert not generate_schedule(sample_courses_info, [], [], params)


def can(sample_courses_info: Sequence[CourseInfo]):
    params = ScheduleParams(
        num_semesters=2,
        min_credits_per_semester=0,
        max_credits_per_semester=1,
        requirement_blocks=[
            [Requirement(
                min_credits=2,
                multi_requirements=[Requirement.base(depts=['CIS'])]
            )],
        ],
        max_double_counts=defaultdict(lambda: None),
        cannot_triple_count=set(),
    )

    # Want to make sure the following cases can't happen:
    # 1. We satisfy the BaseRequirement with one 1CU course, 
    #    and then satisfy the >= 2CU requirement with half-credits
    # 2. We satisfy the CIS elective requirement "twice" with two 1CU
    #    courses to satisfy the >= 2CU requirement
    assert not generate_schedule(sample_courses_info, [], [], params)


# TODO: left to test
# - multiple requirements per block
# - more complex prerequisites
# - more complex double counting
# - requirements that can be satisfied in multiple ways
# - requirements that require both category and department to satisfy