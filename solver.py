from collections import defaultdict
from tkinter.font import BOLD
from typing import Optional, Sequence
from ortools.sat.python import cp_model
from cp2_types import (
    BaseRequirement, CourseInfo, Requirement, ScheduleParams, CompletedCourse, CourseRequest, Schedule, Id, Index, Semester, BoolVar, Uid
)

PRECOLLEGE_SEM: Index = 0

def generate_schedule(
    all_courses: Sequence[CourseInfo],
    course_requests: list[CourseRequest],
    completed_courses: list[CompletedCourse],
    schedule_params: ScheduleParams,
    verbose: bool = False,
) -> Optional[tuple[Schedule, dict[Id, list[tuple[Index, BaseRequirement]]]]]:
    """ Attempt to generate a schedule from the inputs and print it. """
    if verbose:
        print('Constructing model...')
    generator = ScheduleGenerator(list(all_courses), course_requests, completed_courses, schedule_params)
    if verbose:
        print('Solving model...')
    if (soln := generator.solve(verbose=verbose)):
        schedule, course_id_to_requirement = soln
    else:
        print('Not possible to generate a schedule that meets the specifications!\n')
        return None

    num_semesters_without_precollege = len(schedule)-1
    courses_taken = set(course for sem in schedule for course in sem)
    course_id_to_course: dict[Id, CourseInfo] = {
        course['id']: course for course in all_courses if course['id'] in courses_taken
    }
    num_courses_taken = sum(len(sem) for sem in schedule)
    total_cu = sum(
        course_id_to_course[c]['credits'] for sem in schedule for c in sem
    )
    if verbose:
        print(f'Solution found ({num_courses_taken} courses / {total_cu} cu in {num_semesters_without_precollege} semesters)')
        print()

        totcu = 0.0
        for s, semester in enumerate(schedule):
            sem_cu = sum(course_id_to_course[course_id]['credits'] for course_id in semester)
            if s == 0:
                print(f'PRE-COLLEGE CREDITS ({len(semester)} / {sem_cu}):')
            else:
                print(f'SEMESTER {s} ({len(semester)} / {sem_cu}):')
            print('------------------')

            for course_id in semester:
                requirement_names = [
                    f'{br}'
                    for (_b, br) in course_id_to_requirement[course_id]
                ]
                requirement_names_str = ', '.join(requirement_names) or '{}'
                cu = course_id_to_course[course_id]['credits']
                totcu += cu
                # Indicate double-counted courses with a star
                maybe_star = '*' if len(requirement_names) > 1 else ''
                print(f'+ {cu}cu ({totcu}) | {maybe_star}{course_id} (counts_for {requirement_names_str})')
            print()

    return schedule, course_id_to_requirement


def compute_double_counts_upper_bound(schedule_params: ScheduleParams, max_base_reqs_to_satisfy: dict[Uid, int]) -> int:
    """ 
    Compute an upper bound on the number of courses that can count for multiple requirements,
    ignoring any actual details about the requirements.
    """
    model = cp_model.CpModel()
    requirement_blocks = schedule_params.requirement_blocks

    # Enforce max double counting between each pair of blocks
    num_double_counts_between: dict[tuple[Index, Index], cp_model.IntVar] = {}
    for b1 in range(len(requirement_blocks)):
        for b2 in range(b1+1, len(requirement_blocks)):
            num_double_counts_between[b1, b2] = model.NewIntVar(0, schedule_params.max_double_counts[b1, b2], '')

    max_total_base_reqs = 0
    max_base_reqs_in_block: dict[Index, int] = {}
    for b, block in enumerate(requirement_blocks):
        max_base_reqs_in_block[b] = sum(max_base_reqs_to_satisfy[req.uid] for req in block)
        max_total_base_reqs += max_base_reqs_in_block[b]

    counts_for: dict[tuple[Index, Index], BoolVar] = {}
    for b, block in enumerate(requirement_blocks):        
        for c in range(max_total_base_reqs):
            counts_for[c, b] = model.NewBoolVar('')
        
        # All requirements are satisfied in each block
        model.Add(
            sum(counts_for[c, b] for c in range(max_total_base_reqs)) == max_base_reqs_in_block[b]
        )

    for b1 in range(len(requirement_blocks)):
        for b2 in range(b1+1, len(requirement_blocks)):    
            double_counts_boolvars = []
            for c in range(max_total_base_reqs):
                double_counts = model.NewBoolVar('')
                double_counts_boolvars.append(double_counts)
                # cf[c, b1] & cf[c, b2] => dc
                model.AddBoolOr([counts_for[c, b1].Not(), counts_for[c, b2].Not(), double_counts])
                # dc => cf[c, b1] & cf[c, b2]
                model.AddImplication(double_counts, counts_for[c, b1])
                model.AddImplication(double_counts, counts_for[c, b2])

            model.Add(num_double_counts_between[b1, b2] == sum(double_counts_boolvars))

    course_double_counts: dict[Index, BoolVar] = {}
    for c in range(max_total_base_reqs):
        course_double_counts[c] = model.NewBoolVar('')
        model.Add(sum(counts_for[c, b] for b in range(len(requirement_blocks))) >= 2).OnlyEnforceIf(course_double_counts[c])
        model.Add(sum(counts_for[c, b] for b in range(len(requirement_blocks))) <= 1).OnlyEnforceIf(course_double_counts[c].Not())

    # Maximize the total number of courses that count for multiple requirements
    model.Maximize(sum(course_double_counts.values()))

    solver = cp_model.CpSolver()
    assert solver.Solve(model) == cp_model.OPTIMAL
    return int(solver.ObjectiveValue())


class ScheduleGenerator:
    """
    Class that handles construction and solving of a CP model to generate a schedule.

    Attributes:

        ===== DATA =====

        `all_courses: list[CourseInfo]`
            A list of data for all courses.

        `all_course_ids: list[Id]`
            A list of each course's id.

        `course_id_to_course: dict[Id, CourseInfo]`
            A map from each course's id to the CourseInfo object.

        `schedule_params: ScheduleParams`
            An object storing the course requirements.
        
        `requirement_blocks: list[RequirementBlock]`
            A list of all requirement blocks.
        
        `all_requirements: list[Requirement]`
            A list of all Requirements (i.e. non-leaves of the requirements tree).

        `all_base_requirements: list[BaseRequirement]`
            A list of all BaseRequirements (i.e. leaves of the requirements tree).
        
        `base_requirements_of_block: list[list[BaseRequirement]]`
            `base_requirements_of_block[b]` contains a list of all BaseRequirements in block b's subtree.

        `base_requirements_lower_bound: int`
            A lower bound on the numebr of BaseRequirements that must be satisfied, assuming each
            Requirement is satisfied using its k smallest sub-requirements.

        `double_counting_courses_upper_bound: int`
            An upper bound on the number of courses that can count for multiple requirements.

        `last_completed_sem`: Index
            The last semester that was already completed.

        `semester_indices: Sequence[Index]`
            A sequence of all semesters excluding the precollege "semester".

        `semester_indices_with_precollege: Sequence[Index]`
            A sequence of all semesters including the precollege "semester".
        
        `semester_indices_in_future: Sequence[Index]`
            A sequence of all semesters starting from the first semester that hasn't been completed yet.


        ===== MODEL =====

        `model: CpModel`    
            The CP model.

        `num_double_counts: IntVar`
            The number of pairs `{base_req_1, base_req_2}` where one course counts for both requirements.
        
        `num_courses_taken: IntVar`
            The total number of courses taken.
    
        `takes_course: dict[Id, BoolVar]`
            `takes_course[course_id]` is True iff the course is taken at any point.

        `takes_course_in_sem: dict[(Id, Index), BoolVar]`
            `takes_course_in_sem[course_id, sem_idx]` is True iff the course is taken in that semester.
        
        `takes_course_by_sem: dict[(Id, Index), BoolVar]`
            `takes_course_by_sem[course_id, sem_idx]` is True iff the course is taken in or before that semester.

        `is_satisfied: dict[Uid, BoolVar]`
            `is_satisfied[req_uid]` is True iff the Requirement is satisfied.
        
        `counts_for: dict[(Id, Uid), BoolVar]`
            `counts_for[course_id, base_req_uid]` is True iff the course is counted to satisfy the BaseRequirement.

    # Model
    max_difficulty: IntVar
    list_difficulties: list[IntVar]
    """

    def __init__(
        self,
        all_courses: list[CourseInfo], 
        course_requests: list[CourseRequest],
        completed_courses: list[CompletedCourse],
        schedule_params: ScheduleParams,
    ) -> None:
        self.model = cp_model.CpModel()

        self.requirement_blocks = schedule_params.requirement_blocks
        self.requirement_block_indices = range(len(schedule_params.requirement_blocks))
        # DFS on the requirements tree
        self.all_requirements: list[Requirement] = []
        self.base_requirements_of_block: list[list[BaseRequirement]] = []
        self.all_base_requirements: list[BaseRequirement] = []
        # None is used as a separator between the subtrees of each block in the DFS stack
        to_visit: list[Optional[Requirement]] = []
        for block in self.requirement_blocks:
            to_visit.append(None)
            to_visit.extend(block)
        to_visit = to_visit[::-1]
        
        while to_visit:
            req = to_visit.pop()
            if req is None:
                self.base_requirements_of_block.append([])
                continue
            
            self.all_requirements.append(req)
            if req.is_multi_requirement:
                to_visit.extend(req.multi_requirements)
            else:
                # decide what TODO about this
                # for course_id in req.base_requirement.courses:
                #     # Make sure all courses that appear in some requirement are in our set of courses
                #     assert course_id in set(c['id'] for c in all_courses), f'Missing course: {course_id}'
                self.base_requirements_of_block[-1].append(req.base_requirement)
                self.all_base_requirements.append(req.base_requirement)

        # optimization to make the model smaller:
        # only need to consider courses that satisfy at least one of our requirements
        # TODO: may also need courses that are prerequisites for courses that satisfy 
        requested_and_completed_ids = set(
            [request.course_id for request in course_requests] + [completed.course_id for completed in completed_courses]
        )
        all_courses = [
            course for course in all_courses
            if course['id'] in requested_and_completed_ids or any(
                br.satisfied_by_course(course)
                for br in self.all_base_requirements
            )
        ]

        self.course_id_to_course = {
            c['id']: c for c in all_courses
        }
        self.all_courses = self.course_id_to_course.values()
        self.all_course_ids = self.course_id_to_course.keys()

        # Use dynamic programming
        min_base_requirements_to_satisfy: dict[Uid, int] = {}
        max_base_requirements_to_satisfy: dict[Uid, int] = {}
        for req in reversed(self.all_requirements):
            if not req.is_multi_requirement:
                min_base_requirements_to_satisfy[req.uid] = 1
                max_base_requirements_to_satisfy[req.uid] = 1
            else:
                min_base_requirements_to_satisfy[req.uid] = sum(sorted(
                    min_base_requirements_to_satisfy[subreq.uid] for subreq in req.multi_requirements
                )[:req.min_satisfied_reqs])
                max_base_requirements_to_satisfy[req.uid] = sum(sorted(
                    (max_base_requirements_to_satisfy[subreq.uid] for subreq in req.multi_requirements),
                    reverse=True
                )[:req.min_satisfied_reqs])

        self.base_requirements_lower_bound = sum(
            min_base_requirements_to_satisfy[req.uid] for block in self.requirement_blocks for req in block
        )

        self.course_requests = course_requests
        self.completed_courses = completed_courses
        self.schedule_params = schedule_params
        self.last_completed_sem = max([course.semester for course in self.completed_courses], default=0)

        # Clean schedule_params.max_double_counts entries that are None (i.e., no limit)
        block_index_pairs = [
            (b1, b2) 
            for b1 in self.requirement_block_indices 
            for b2 in range(b1 + 1, len(self.requirement_block_indices))
        ]
        for b1, b2 in block_index_pairs:
            if schedule_params.max_double_counts[b1, b2] is None:
                # If we have unlimited double counts, we can upper bound the number of double counts with
                # an upper bound on the number of BaseRequirements in either block (whichever is smaller)
                requirement_blocks = self.schedule_params.requirement_blocks
                min_block_size = min(len(requirement_blocks[b1]), len(requirement_blocks[b2]))
                schedule_params.max_double_counts[b1, b2] = min_block_size

        self.double_counting_courses_upper_bound = compute_double_counts_upper_bound(schedule_params, max_base_requirements_to_satisfy)

        self.semester_indices = range(1, schedule_params.num_semesters+1)
        self.semester_indices_with_precollege = range(schedule_params.num_semesters+1)
        self.semester_indices_in_future = range(self.last_completed_sem+1, schedule_params.num_semesters+1)

        self.create_cp_vars()
        constraints = [
            self.link_takes_course_vars,
            self.link_satisfies_vars,
            self.satisfy_all_requirements_once,
            self.enforce_max_courses_per_semester,
            self.enforce_min_courses_per_semester,
            self.enforce_double_counting_rules,
            self.take_courses_at_most_once,
            self.must_take_course_to_count,
            self.courses_only_satisfy_requirements,
            self.no_double_counting_within_requirement_blocks,
            self.dont_take_unnecessary_courses,
            self.enforce_prerequisites,
            self.take_requested_courses,
            self.too_many_courses_infeasible,
            self.take_completed_courses,
            # self.minimize_maximum_difficulty,
            self.dont_take_cross_listed_twice
        ]
        for constraint in constraints:
            constraint()

    def solve(self, num_threads=8, verbose=False) -> Optional[tuple[Schedule, dict[Id, list[tuple[Index, BaseRequirement]]]]]:
        """
        Solve the model to return a schedule along with a mapping from each course Id c
        to a list of indices (b, r), indicating that course c satisfies requirement r
        of block b in the SemesterRequirements.
        """
        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = num_threads
        print(f'Model has {len(self.model.Proto().variables)} vars and {len(self.model.Proto().constraints)} constraints')
        res = solver.Solve(self.model)
        if verbose:
            print(solver.ResponseStats())

        if res in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            schedule: Schedule = []
            course_ids_to_satisfied_block_req_indices: dict[Id, list[tuple[Index, BaseRequirement]]] = {}
            for s in self.semester_indices_with_precollege:
                selected_course_ids: list[Id] = [
                    c for c in self.all_course_ids
                    if solver.Value(self.takes_course_in_sem[c, s]) == 1
                ]
                schedule.append(selected_course_ids)
                course_ids_to_satisfied_block_req_indices |= {
                    c: [
                        (b, br)
                        for b in self.requirement_block_indices
                        for br in self.base_requirements_of_block[b]
                        if solver.Value(self.counts_for[c, br.uid]) == 1
                    ]
                    for c in selected_course_ids
                }

            return schedule, course_ids_to_satisfied_block_req_indices

        else:
            return None

    def create_cp_vars(self) -> None:
        """ Initialize all CP variables. """
        model = self.model

        # number of times we double count
        self.num_double_counts = model.NewIntVar(0, sum(self.schedule_params.max_double_counts.values()), '')
        # takes_course_in_sem[c, s] is true iff we take c in semester s
        self.takes_course_in_sem: dict[tuple[Id, Index], BoolVar] = {
            (c, s): model.NewBoolVar('') 
            for c in self.all_course_ids 
            for s in self.semester_indices_with_precollege
        }
        # takes_course[c] is true iff we take c in any semester
        self.takes_course: dict[Id, BoolVar] = {
            c: model.NewBoolVar('') 
            for c in self.all_course_ids 
        }
        # takes_course_by_sem[c, s] is true if we take c in semester s or earlier
        self.takes_course_by_sem: dict[tuple[Id, Index], BoolVar] = {
            (c, s): model.NewBoolVar('') 
            for c in self.all_course_ids 
            for s in self.semester_indices_with_precollege
        }
        # counts_for[c, r] is true iff course c counts for BaseRequirement r
        self.counts_for: dict[tuple[Id, Uid], BoolVar] = {
            (c, br.uid): model.NewBoolVar('')
            for c in self.all_course_ids
            for br in self.all_base_requirements
        }
        # is_satisfied[r] is true if Requirement r is satisfied
        self.is_satisfied: dict[Uid, BoolVar] = {
            r.uid: model.NewBoolVar('')
            for r in self.all_requirements
        }

    def link_takes_course_vars(self) -> None:
        """ Reify `takes_course` and `takes_course_by_sem` in terms of `takes_course_in_sem`. """
        model = self.model
        for c in self.all_course_ids:
            model.AddBoolOr([
                self.takes_course_in_sem[c, s]
                for s in self.semester_indices_with_precollege
            ]).OnlyEnforceIf(
                self.takes_course[c]
            )
            model.AddBoolAnd([
                self.takes_course_in_sem[c, s].Not()
                for s in self.semester_indices_with_precollege
            ]).OnlyEnforceIf(
                self.takes_course[c].Not()
            )
        
            # TODO: could try the quadratic approach to this and see how it fares
            # Reify takes_course_by_sem in terms of takes_course_in_sem
            # TODO: actually just change this to use implications/bools
            model.Add(self.takes_course_by_sem[c, PRECOLLEGE_SEM] == self.takes_course_in_sem[c, PRECOLLEGE_SEM])
            for s in self.semester_indices:
                model.AddBoolOr([
                    self.takes_course_by_sem[c, s-1], self.takes_course_in_sem[c, s]
                ]).OnlyEnforceIf(self.takes_course_by_sem[c, s])
                model.AddBoolAnd([
                    self.takes_course_by_sem[c, s-1].Not(), self.takes_course_in_sem[c, s].Not()
                ]).OnlyEnforceIf(self.takes_course_by_sem[c, s].Not())

    def link_satisfies_vars(self) -> None:
        """ Reify `is_satisfied` in terms of `counts_for`. """
        model = self.model
        for r0 in self.all_requirements:
            if r0.is_multi_requirement:
                model.Add(
                    sum(self.is_satisfied[r.uid] for r in r0.multi_requirements) 
                    >= 
                    r0.min_satisfied_reqs
                ).OnlyEnforceIf(self.is_satisfied[r0.uid])
                model.Add(
                    sum(self.is_satisfied[r.uid] for r in r0.multi_requirements) 
                    <
                    r0.min_satisfied_reqs
                ).OnlyEnforceIf(self.is_satisfied[r0.uid].Not())

            else:
                br = r0.base_requirement
                # br satisfied ==> some course counts for br
                model.AddBoolOr(
                    [self.is_satisfied[r0.uid].Not()]
                    + [self.counts_for[c, br.uid] for c in self.all_course_ids]
                )
                # some course counts for br ==> br satisfied
                for c in self.all_course_ids:
                    model.AddImplication(self.counts_for[c, br.uid], self.is_satisfied[r0.uid])

    def satisfy_all_requirements_once(self) -> None:
        """ All requirements must be satisfied by exactly one course. """
        model = self.model
        for block in self.requirement_blocks:
            for r in block:
                # All top-level requirements must be satisfied
                model.Add(
                    self.is_satisfied[r.uid] == 1
                )
                # Redundant: Top-level BaseRequirements should be satisfied by exactly one course
                if not r.is_multi_requirement:
                    br = r.base_requirement
                    model.Add(
                        sum(self.counts_for[c, br.uid] for c in self.all_course_ids) == 1
                    )
        
    def enforce_max_courses_per_semester(self) -> None:
        """ Limit the maximum number of courses per semester based on the schedule params. """
        model = self.model

        for s in self.semester_indices_in_future:
            model.Add(
                sum(self.takes_course_in_sem[c, s] for c in self.all_course_ids)
                <= 
                self.schedule_params.max_courses_per_semester
            )

    def enforce_min_courses_per_semester(self) -> None:
        """ Limit the minimum number of courses per semester based on the schedule params. """
        model = self.model

        for s in self.semester_indices_in_future:
            model.Add(
                sum(self.takes_course_in_sem[c, s] for c in self.all_course_ids)
                >=
                self.schedule_params.min_courses_per_semester
            )

    def enforce_double_counting_rules(self) -> None:
        """ Limit the number of courses that can be double counted based on the schedule params. """
        model = self.model
        # total number of courses >= total number of requirements - num_double_counts
        # this formula is derived from the inclusion-exclusion principle (cis160 ftw)

        double_counts_boolvars_between: defaultdict[tuple[Index, Index], list[BoolVar]]
        double_counts_boolvars_between = defaultdict(list)

        for c in self.all_course_ids:
            # Disallow triple counting for requirements that cannot triple count
            total_num_times_counted = model.NewIntVar(0, 2, '')
            model.Add(
                total_num_times_counted == sum(
                    self.counts_for[c, br.uid] 
                    for b in self.requirement_block_indices
                    if b in self.schedule_params.cannot_triple_count
                    for br in self.base_requirements_of_block[b]
                )
            )

            # Count the number of double counts between each pair of blocks
            for b1, b2 in self.schedule_params.max_double_counts.keys():
                num_times_counted_in_either_block = model.NewIntVar(0, 2, '')
                model.Add(
                    num_times_counted_in_either_block == sum(
                        self.counts_for[c, br.uid]
                        for b in [b1, b2]
                        for br in self.base_requirements_of_block[b]
                    )
                )
                is_double_counted = model.NewBoolVar('')
                model.Add(num_times_counted_in_either_block == 2).OnlyEnforceIf(is_double_counted)
                model.Add(num_times_counted_in_either_block != 2).OnlyEnforceIf(is_double_counted.Not())
                double_counts_boolvars_between[b1, b2].append(is_double_counted)

        # Allow at most max_double_counts[b1, b2] courses to double count between blocks b1 and b2
        for (b1, b2), max_double_counts in self.schedule_params.max_double_counts.items():
            num_double_counts_between_blocks = model.NewIntVar(0, max_double_counts, '')
            model.Add(
                num_double_counts_between_blocks == sum(double_counts_boolvars_between[b1, b2])
            )

        # note: this is just the definition of num_double_counts
        model.Add(self.num_double_counts == sum(sum(l) for l in double_counts_boolvars_between.values()))

    def take_courses_at_most_once(self) -> None:
        """ We should only take a course at most once. """
        model = self.model
        for c in self.all_course_ids:
            model.Add(
                sum(self.takes_course_in_sem[c, s] for s in self.semester_indices_with_precollege) <= 1
            )

    def must_take_course_to_count(self) -> None:
        """ If we do not take a course, then it does not satisfy anything. """
        model = self.model
        for c in self.all_course_ids:
            for br in self.all_base_requirements:
                model.AddImplication(
                    self.takes_course[c].Not(), 
                    self.counts_for[c, br.uid].Not()
                )

    def courses_only_satisfy_requirements(self) -> None:
        """ A course cannot satisfy anything that it is not allowed to. """
        model = self.model
        course_counts_for = {}
        for completed_id, _, completed_id_counts_for in self.completed_courses:
            course_counts_for[completed_id] = set(completed_id_counts_for)
        for course in self.all_courses:
            c = course['id']
            for br in self.all_base_requirements:
                if not br.satisfied_by_course(course) and br.uid not in course_counts_for.get(c, []):
                    model.Add(self.counts_for[c, br.uid] == 0)

    def no_double_counting_within_requirement_blocks(self) -> None:
        """ A course can only count once within a single block of requirements. """
        model = self.model
        
        for c in self.all_course_ids:           
            for b in self.requirement_block_indices:
                model.Add(
                    sum(self.counts_for[c, br.uid] for br in self.base_requirements_of_block[b]) <= 1
                )

    def dont_take_unnecessary_courses(self) -> None:
        """ If a course won't satisfy any requirements, don't take it. """
        # TODO: what about prereqs that don't count for anything?
        model = self.model
        taken_courses = set(course.course_id for course in self.completed_courses)
        requested_courses = set(course.course_id for course in self.course_requests)
        for c in self.all_course_ids:
            # TODO: commenting this out because we can assume for now all taken courses
            # count for something -- otherwise we can ask user to label them, or maybe
            # just try to minimize total number of courses taken
            # if course_id in taken_courses:
            #     # Don't add this constraint if the user has already taken the course
            #     continue

            if c in requested_courses:
                # Don't add this constraint if the user has requested this course
                continue

            # TODO: change this to use implications/bools?
            course_counts_for_something = model.NewBoolVar('')
            model.AddBoolOr([
                self.counts_for[c, br.uid] 
                for br in self.all_base_requirements
            ]).OnlyEnforceIf(course_counts_for_something)
            model.AddBoolAnd([
                self.counts_for[c, br.uid].Not()
                for br in self.all_base_requirements
            ]).OnlyEnforceIf(course_counts_for_something.Not())
            model.AddImplication(course_counts_for_something.Not(), self.takes_course[c].Not())

    def enforce_prerequisites(self) -> None:
        """ If we have taken some course by sem s, we must have taken its prereqs by sem s-1. """
        # TODO: allow a mechanism for ignoring prereqs
        model = self.model
        taken_courses = set(course.course_id for course in self.completed_courses)
        for course in self.all_courses:
            c = course['id']
            if c in taken_courses:
                continue
            for or_prereqs in course['prerequisites']:
                # Ignore prereqs in or_prereqs that we don't have an entry for
                or_prereq_ids = [
                    prereq_id
                    for prereq_id in or_prereqs
                    if prereq_id in self.course_id_to_course
                ]
                for s in self.semester_indices:
                    or_prereqs_satisfied = model.NewBoolVar('')
                    model.AddBoolOr([
                        self.takes_course_by_sem[p, s-1]
                        for p in or_prereq_ids
                    ]).OnlyEnforceIf(or_prereqs_satisfied)
                    model.AddBoolAnd([
                        self.takes_course_by_sem[p, s-1].Not()
                        for p in or_prereq_ids
                    ]).OnlyEnforceIf(or_prereqs_satisfied.Not())
                    model.AddImplication(self.takes_course_in_sem[c, s], or_prereqs_satisfied)

    def take_requested_courses(self) -> None:
        """ Take the courses that the student requested. """
        model = self.model

        completed_ids = set(course.course_id for course in self.completed_courses)

        for course_id, sem in self.course_requests:
            # skip courses already taken/semesters already taken
            if sem and sem <= self.last_completed_sem:
                continue
            if course_id in completed_ids:
                continue

            if sem:
                model.Add(
                    self.takes_course_in_sem[course_id, sem] == 1
                )
            else:
                model.Add(
                    self.takes_course[course_id] == 1
                )

    def too_many_courses_infeasible(self) -> None:
        """ Give the model some helpful facts to recognize schedules with too many courses to be infeasible. """
        model = self.model
        num_semesters = self.schedule_params.num_semesters
        max_courses_per_semester = self.schedule_params.max_courses_per_semester

        num_courses_ub = len(self.completed_courses) + max_courses_per_semester * (num_semesters - self.last_completed_sem)
        self.num_courses_taken = model.NewIntVar(0, num_courses_ub, '')
        model.Add(
            self.num_courses_taken == sum(self.takes_course[c] for c in self.all_course_ids)
        )
        print(
            f'{num_courses_ub} >= num_courses_taken >= {self.base_requirements_lower_bound} - {self.double_counting_courses_upper_bound}'
        )
        model.Add(
            self.num_courses_taken >= (self.base_requirements_lower_bound - self.double_counting_courses_upper_bound)
        )
    
    def take_completed_courses(self) -> None:
        """ Take the courses that the student has already completed. """
        model = self.model
        for course_id, sem, counts_for in self.completed_courses:
            model.Add(
                self.takes_course_in_sem[course_id, sem] == 1
            )
            for br_uid in counts_for:
                model.Add(
                    self.counts_for[course_id, br_uid] == 1
                )

        # disallow taking any other courses in semesters that have already gone by
        for sem in range(PRECOLLEGE_SEM, self.last_completed_sem + 1):
            for course_id in self.all_course_ids:

                # skip existing courses
                add_constraint = True
                for course in self.completed_courses:
                    if course_id == course.course_id and course.semester == sem:
                        add_constraint = False
                
                if add_constraint:
                    model.Add(
                        self.takes_course_in_sem[course_id, sem] == 0
                    )
        
    def dont_take_cross_listed_twice(self) -> None:
        """ Enforce cross-listing across courses """
        model = self.model

        for course in self.all_courses:
            c = course['id']
            crosslistings = course["crosslistings"]

            # get all crosslisted courses indices
            cross_listing_ids = [
                crosslisted_id
                for crosslisted_id in crosslistings
                if crosslisted_id in self.course_id_to_course
            ]

            for cross_listed_course in cross_listing_ids:
                model.AddImplication(
                    self.takes_course[c], 
                    self.takes_course[cross_listed_course].Not())

    def take_course_only_when_offered(self) -> None:
        """ 
        Don't take a class if in some semester if, based on recent history,
        it is not offered in that season.
        """
        # TODO: allow override with course requests?
        for s in self.semester_indices_in_future:
            season = Semester.SPRING if s % 2 else Semester.FALL
            for course in self.all_courses:
                c = course['id']
                rate_offered_in_season = course['rate_offered'][season.value]
                if rate_offered_in_season == 0:
                    self.model.Add(
                        self.takes_course_in_sem[c, s] == 0
                    )

    def minimize_maximum_difficulty(self) -> None:
        """ Main optimizer: based on creating a balanced academic load """
        model = self.model

        # get upper bound for maximum difficulty
        upper_bound = 4 * self.schedule_params.max_courses_per_semester * self.schedule_params.num_semesters
        self.max_difficulty = model.NewIntVar(0, upper_bound, '')

        # only iterate for semesters left
        self.list_difficulties = [model.NewIntVar(0, 4 * self.schedule_params.max_courses_per_semester, '') for _ in range(self.schedule_params.num_semesters)]

        for s in range(self.last_completed_sem + 1, self.schedule_params.num_semesters + 1):
            model.Add(
                self.list_difficulties[s - 1] 
                == sum(
                    round(difficulty) * self.takes_course_in_sem[course['id'], s]
                    for course in self.all_courses
                    if (difficulty := course.get("difficulty", 0) or 0) >= 0
                )
            )
        
        # minimize maximum difficulty across semesters
        model.AddMaxEquality(self.max_difficulty, self.list_difficulties)
        model.Minimize(self.max_difficulty)
    

            
                 

