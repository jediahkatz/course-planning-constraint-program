from collections import defaultdict
from typing import Optional
from typing_extensions import IntVar
from ortools.sat.python import cp_model
from cp2_types import (
    CourseInfo, ScheduleParams, CompletedClasses, CourseRequest, Schedule, Id, Index, VarMap1D, VarMap2D, VarMap3D
)

PRECOLLEGE_SEM: Index = 0

def generate_schedule(
    all_courses: list[CourseInfo],
    course_requests: list[CourseRequest],
    completed_courses: list[CompletedClasses],
    schedule_params: ScheduleParams,
    verbose: bool = False,
) -> Optional[tuple[Schedule, dict[Id, list[tuple[Index, Index]]]]]:
    """ Attempt to generate a schedule from the inputs and print it. """
    if verbose:
        print('Constructing model...')
    generator = ScheduleGenerator(all_courses, course_requests, completed_courses, schedule_params)
    if verbose:
        print('Solving model...')
    if (soln := generator.solve(verbose=verbose)):
        schedule, course_id_to_requirement_index = soln
    else:
        print('Not possible to generate a schedule that meets the specifications!\n')
        return None

    num_semesters_without_precollege = len(schedule)-1
    num_courses_taken = sum(len(sem) for sem in schedule)
    if verbose:
        print(f'Solution found ({num_courses_taken} courses in {num_semesters_without_precollege} semesters)')
        print()

        for s, semester in enumerate(schedule):
            if s == 0:
                print('PRE-COLLEGE CREDITS:')
            else:
                print(f'SEMESTER {s}:')
            print('------------------')

            for course_id in semester:
                requirement_names = [
                    str(schedule_params.requirement_blocks[b][r])
                    for (b, r) in course_id_to_requirement_index[course_id]
                ]
                requirement_names_str = ', '.join(requirement_names)
                # Indicate double-counted courses with a star
                maybe_star = '*' if len(requirement_names) > 1 else ''
                print(f'+ {maybe_star}{course_id} (satisfies {requirement_names_str})')
            print()

    return schedule, course_id_to_requirement_index


class ScheduleGenerator:
    """
    Class that handles construction and solving of a CP model to generate a schedule.

    Attributes:
        `model: CpModel`    
            The CP model.

        `all_courses: list[CourseInfo]`
            A list of data for all courses.

        TODO...
    """
    # Data
    all_courses: list[CourseInfo]
    course_id_to_index: dict[Id, Index]
    schedule_params: ScheduleParams
    precollege_credits: set[Id]
    course_indices: range
    semester_indices: range
    semester_indices_with_precollege: range
    requirement_block_indices: range
    requirement_indices_of_block: list[range]
    
    # Model
    model: cp_model.CpModel
    num_double_counts: cp_model.IntVar
    num_courses_taken: cp_model.IntVar
    max_difficulty: cp_model.IntVar
    list_difficulties: list[cp_model.IntVar]
    takes_course: VarMap1D
    takes_course_in_sem: VarMap2D
    takes_course_by_sem: VarMap2D
    is_satisfied: VarMap2D
    satisfies: VarMap3D

    def __init__(
        self,
        all_courses: list[CourseInfo], 
        course_requests: list[CourseRequest],
        completed_courses: list[CompletedClasses],
        schedule_params: ScheduleParams,
    ) -> None:
        self.model = cp_model.CpModel()
        self.all_courses = all_courses
        self.course_id_to_index = {course_id['id']: c for c, course_id in enumerate(all_courses)}
        self.course_indices = range(len(all_courses))
        self.requirement_block_indices = range(len(schedule_params.requirement_blocks))
        self.requirement_indices_of_block = [
            range(len(schedule_params.requirement_blocks[b])) for b in self.requirement_block_indices
        ]
        self.course_requests = course_requests
        self.completed_courses = completed_courses
        self.precollege_credits = set(
            course.course_id for course in completed_courses if course.semester == PRECOLLEGE_SEM
        )
        self.schedule_params = schedule_params
        # Clean schedule_params.max_double_counts entries that are None (i.e., no limit)
        block_index_pairs = [
            (b1, b2) 
            for b1 in self.requirement_block_indices 
            for b2 in range(b1 + 1, len(self.requirement_block_indices))
        ]
        for b1, b2 in block_index_pairs:
            if schedule_params.max_double_counts[b1, b2] is None:
                # If we have unlimited double counts, we can upper bound by the smaller block size
                requirement_blocks = self.schedule_params.requirement_blocks
                min_block_size = min(len(requirement_blocks[b1]), len(requirement_blocks[b2]))
                schedule_params.max_double_counts[b1, b2] = min_block_size

        self.semester_indices = range(1, schedule_params.num_semesters+1)
        self.semester_indices_with_precollege = range(schedule_params.num_semesters+1)
        self.create_cp_vars()
        constraints = [
            self.link_takes_course_vars,
            self.link_satisfies_vars,
            self.satisfy_all_requirements_once,
            self.enforce_max_courses_per_semester,
            self.enforce_double_counting_rules,
            self.take_courses_at_most_once,
            self.must_take_course_to_count,
            self.courses_only_satisfy_requirements,
            self.no_double_counting_within_requirement_blocks,
            self.dont_take_unnecessary_courses,
            self.enforce_prerequisites,
            self.take_requested_courses,
            self.dont_assign_precollege_semester,
            self.too_many_courses_infeasible,
            self.take_completed_courses,
            self.take_min_amount_of_courses_per_semester,
            self.minimize_maximum_difficulty,
            self.dont_take_cross_listed_twice
        ]
        for constraint in constraints:
            constraint()

    def solve(self, num_threads=8, verbose=False) -> Optional[tuple[Schedule, dict[Id, list[tuple[Index, Index]]]]]:
        """
        Solve the model to return a schedule along with a mapping from each course Id c
        to a list of indices (b, r), indicating that course c satisfies requirement r
        of block b in the SemesterRequirements.
        """
        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = num_threads
        res = solver.Solve(self.model)
        if verbose:
            print(solver.ResponseStats())
        if res in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            schedule: Schedule = []
            course_ids_to_satisfied_block_req_indices: dict[Id, list[tuple[Index, Index]]] = {}
            for s in self.semester_indices_with_precollege:
                selected_course_indices: list[Index] = [
                    c for c in self.course_indices
                    if solver.Value(self.takes_course_in_sem[c, s]) == 1
                ]
                schedule.append(
                    [self.all_courses[c]['id'] for c in selected_course_indices]
                )
                course_ids_to_satisfied_block_req_indices |= {
                    self.all_courses[c]['id']: [
                        (b, r)
                        for b in self.requirement_block_indices
                        for r in self.requirement_indices_of_block[b]
                        if solver.Value(self.satisfies[c, b, r]) == 1
                    ]
                    for c in selected_course_indices
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
        self.takes_course_in_sem = {
            (c, s): model.NewBoolVar('') 
            for c in self.course_indices 
            for s in self.semester_indices_with_precollege
        }
        # takes_course[c] is true iff we take c in any semester
        self.takes_course = {
            c: model.NewBoolVar('') 
            for c in self.course_indices 
        }
        # takes_course_by_sem[c, s] is true if we take c in semester s or earlier
        self.takes_course_by_sem = {
            (c, s): model.NewBoolVar('') 
            for c in self.course_indices 
            for s in self.semester_indices_with_precollege
        }
        # satisfies[c, b, r] is true iff course c satisfies requirements[r] for block b
        self.satisfies = {
            (c, b, r): model.NewBoolVar('')
            for c in self.course_indices
            for b in self.requirement_block_indices
            for r in self.requirement_indices_of_block[b]
        }
        # is_satisfied[b, r] is true if requirements[r] for block b is satisfied
        self.is_satisfied = {
            (b, r): model.NewBoolVar('')
            for b in self.requirement_block_indices
            for r in self.requirement_indices_of_block[b]
        }

    def link_takes_course_vars(self) -> None:
        """ Reify `takes_course` and `takes_course_by_sem` in terms of `takes_course_in_sem`. """
        model = self.model
        for c in self.course_indices:
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
            model.Add(self.takes_course_by_sem[c, PRECOLLEGE_SEM] == self.takes_course_in_sem[c, PRECOLLEGE_SEM])
            for s in self.semester_indices:
                model.AddBoolOr([
                    self.takes_course_by_sem[c, s-1], self.takes_course_in_sem[c, s]
                ]).OnlyEnforceIf(self.takes_course_by_sem[c, s])
                model.AddBoolAnd([
                    self.takes_course_by_sem[c, s-1].Not(), self.takes_course_in_sem[c, s].Not()
                ]).OnlyEnforceIf(self.takes_course_by_sem[c, s].Not())

    def link_satisfies_vars(self) -> None:
        """ Reify `is_satisfied` in terms of `satisfies`. """
        model = self.model
        for b in self.requirement_block_indices:
            for r in self.requirement_indices_of_block[b]:
                model.AddBoolOr([
                    self.satisfies[c, b, r] for c in self.course_indices
                ]).OnlyEnforceIf(
                    self.is_satisfied[b, r]
                )
                
                model.AddBoolAnd([
                    self.satisfies[c, b, r].Not() for c in self.course_indices
                ]).OnlyEnforceIf(
                    self.is_satisfied[b, r].Not()
                )

    def satisfy_all_requirements_once(self) -> None:
        """ All requirements must be satisfied by exactly one course. """
        model = self.model
        for b in self.requirement_block_indices:
            for r in self.requirement_indices_of_block[b]:
                # A requirement should be satisfied by exactly one course
                model.Add(
                    sum(self.satisfies[c, b, r] for c in self.course_indices) == 1
                )
                # Redundant: all requirements must be satisfied
                model.Add(
                    self.is_satisfied[b, r] == 1
                )
        
    def enforce_max_courses_per_semester(self) -> None:
        """ Limit the maximum number of courses per semester based on the schedule params. """
        model = self.model

        max_sem = max([course.semester for course in self.completed_courses], default=0)

        for s in range(max_sem + 1, len(self.semester_indices) + 1):
            model.Add(
                sum(self.takes_course_in_sem[c, s] for c in self.course_indices)
                <= 
                self.schedule_params.max_courses_per_semester
            )

    def enforce_double_counting_rules(self) -> None:
        """ Limit the number of courses that can be double counted based on the schedule params. """
        model = self.model
        # possible future BUG: if we ever allow triple counting, then need to change equation below:
        # total number of courses = total number of requirements - num_double_counts

        double_counts_boolvars_between: defaultdict[tuple[Index, Index], list[cp_model.IntVar]]
        double_counts_boolvars_between = defaultdict(list)

        for c in self.course_indices:
            # Disallow triple counting
            total_num_times_counted = model.NewIntVar(0, 2, '')
            model.Add(
                total_num_times_counted == sum(
                    self.satisfies[c, b, r] 
                    for b in self.requirement_block_indices
                    for r in self.requirement_indices_of_block[b]
                )
            )

            # Count the number of double counts between each pair of blocks
            for b1, b2 in self.schedule_params.max_double_counts.keys():
                num_times_counted_in_either_block = model.NewIntVar(0, 2, '')
                model.Add(
                    num_times_counted_in_either_block == sum(
                        self.satisfies[c, b, r]
                        for b in [b1, b2]
                        for r in self.requirement_indices_of_block[b]
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
        for c in self.course_indices:
            model.Add(
                sum(self.takes_course_in_sem[c, s] for s in self.semester_indices) <= 1
            )

    def must_take_course_to_count(self) -> None:
        """ If we do not take a course, then it does not satisfy anything. """
        model = self.model
        for c in self.course_indices:
            for b in self.requirement_block_indices:
                for r in self.requirement_indices_of_block[b]:
                    model.AddImplication(
                        self.takes_course[c].Not(), 
                        self.satisfies[c, b, r].Not()
                    )

    def courses_only_satisfy_requirements(self) -> None:
        """ A course cannot satisfy anything that it is not allowed to. """
        model = self.model
        for c, course in enumerate(self.all_courses):
            for b in self.requirement_block_indices:
                for r, req in enumerate(self.schedule_params.requirement_blocks[b]):
                    if not req.satisfied_by_course(course):
                        model.Add(self.satisfies[c, b, r] == 0)

    def no_double_counting_within_requirement_blocks(self) -> None:
        """ A course can only count once within a single block of requirements. """
        model = self.model
        
        for c in self.course_indices:           
            for b in self.requirement_block_indices:
                model.Add(
                    sum(self.satisfies[c, b, r] for r in self.requirement_indices_of_block[b]) <= 1
                )

    def dont_take_unnecessary_courses(self) -> None:
        """ If a course won't satisfy any requirements, don't take it. """
        model = self.model
        taken_courses = set(course.course_id for course in self.completed_courses)
        requested_courses = set(course.course_id for course in self.course_requests)
        for c in self.course_indices:
            course_id = self.all_courses[c]['id']
            if course_id in taken_courses:
                # Don't add this constraint if the user has already taken the course
                continue

            if course_id in requested_courses:
                # Don't add this constraint if the user has requested this course
                continue

            course_satisfies_something = model.NewBoolVar('')
            model.AddBoolOr([
                self.satisfies[c, b, r] 
                for b in self.requirement_block_indices
                for r in self.requirement_indices_of_block[b]
            ]).OnlyEnforceIf(course_satisfies_something)
            model.AddBoolAnd([
                self.satisfies[c, b, r].Not()
                for b in self.requirement_block_indices
                for r in self.requirement_indices_of_block[b]
            ]).OnlyEnforceIf(course_satisfies_something.Not())
            model.AddImplication(course_satisfies_something.Not(), self.takes_course[c].Not())

    def enforce_prerequisites(self) -> None:
        """ If we have taken some course by sem s, we must have taken its prereqs by sem s-1. """
        # TODO: allow a mechanism for ignoring prereqs
        model = self.model
        taken_courses = set(course.course_id for course in self.completed_courses)
        for c, course in enumerate(self.all_courses):
            if course['id'] in taken_courses:
                continue
            for or_prereqs in course['prerequisites']:
                # Ignore prereqs in or_prereqs that we don't have an entry for
                or_prereqs_indices = [
                    self.course_id_to_index.get(prereq_id)
                    for prereq_id in or_prereqs
                    if self.course_id_to_index.get(prereq_id) is not None
                ]
                for s in self.semester_indices:
                    or_prereqs_satisfied = model.NewBoolVar('')
                    model.AddBoolOr([
                        self.takes_course_by_sem[p, s-1]
                        for p in or_prereqs_indices
                    ]).OnlyEnforceIf(or_prereqs_satisfied)
                    model.AddBoolAnd([
                        self.takes_course_by_sem[p, s-1].Not()
                        for p in or_prereqs_indices
                    ]).OnlyEnforceIf(or_prereqs_satisfied.Not())
                    model.AddImplication(self.takes_course_in_sem[c, s], or_prereqs_satisfied)

    def take_requested_courses(self) -> None:
        """ Take the courses that the student requested. """
        model = self.model

        max_sem = max([course.semester for course in self.completed_courses], default=-1)
        completed_ids = set(course.course_id for course in self.completed_courses)

        for course_id, sem in self.course_requests:
            # skip courses already taken/semesters already taken
            if sem <= max_sem:
                continue
            
            if course_id in completed_ids:
                continue

            # skip precollege credits
            if sem == 0:
                continue

            model.Add(
                self.takes_course_in_sem[self.course_id_to_index[course_id], sem] == 1
            )

    def dont_assign_precollege_semester(self) -> None:
        """ Don't schedule any pre-college credits except for the ones the user populated. """
        model = self.model
        for c, course in enumerate(self.all_courses):
            if course['id'] not in self.precollege_credits:
                model.Add(
                    self.takes_course_in_sem[c, PRECOLLEGE_SEM] == 0
                )

    def too_many_courses_infeasible(self) -> None:
        """ Give the model some helpful facts to recognize schedules with too many courses to be infeasible. """
        model = self.model
        num_semesters = self.schedule_params.num_semesters
        max_courses_per_semester = self.schedule_params.max_courses_per_semester

        num_courses_ub = num_semesters * max_courses_per_semester + len(self.precollege_credits)
        self.num_courses_taken = model.NewIntVar(0, num_courses_ub, '')
        model.Add(
            self.num_courses_taken == sum(self.takes_course[c] for c in self.course_indices)
        )
        total_num_requirements = sum(len(block) for block in self.schedule_params.requirement_blocks)
        model.Add(
            self.num_courses_taken >= total_num_requirements - self.num_double_counts
        )
    
    def take_completed_courses(self) -> None:
        """ Take the courses that the student has already completed. """
        model = self.model
        for course_id, sem in self.completed_courses:
            model.Add(
                self.takes_course_in_sem[self.course_id_to_index[course_id], sem] == 1
            )

        # disallow taking any other courses in semesters that have already gone by
        max_sem = max([course.semester for course in self.completed_courses], default=0)
        for sem in range(1, max_sem + 1):
            for c in self.course_indices:

                # skip existing courses
                add_constraint = True
                course_id = self.all_courses[c]['id']
                for course in self.completed_courses:
                    if course_id == course.course_id and course.semester == sem:
                        add_constraint = False
                
                if add_constraint:
                    model.Add(
                        self.takes_course_in_sem[c, sem] == 0
                    )
        
    def take_min_amount_of_courses_per_semester(self) -> None:
        """ Take a baseline amount of courses per sem """
        model = self.model

        max_sem = max([course.semester for course in self.completed_courses], default=0)

        for s in range(max_sem + 1, len(self.semester_indices) + 1):
            model.Add(
                sum(self.takes_course_in_sem[c, s] for c in self.course_indices)
                >=
                self.schedule_params.min_courses_per_semester
            )
    
    def minimize_maximum_difficulty(self) -> None:
        """ main optimizer: based on creating a balanced academic load """
        model = self.model

        # get upper bound for maximum difficulty
        upper_bound = 4 * self.schedule_params.max_courses_per_semester * self.schedule_params.num_semesters
        self.max_difficulty = model.NewIntVar(0, upper_bound, '')

        # only iterate for semesters left
        max_sem = max([course.semester for course in self.completed_courses], default=0)
        self.list_difficulties = [model.NewIntVar(0, 4 * self.schedule_params.max_courses_per_semester, '') for _ in range(len(self.semester_indices))]

        for s in range(max_sem + 1, len(self.semester_indices) + 1):
            model.Add(
                self.list_difficulties[s - 1] == sum(round(self.all_courses[c]["difficulty"] if self.all_courses[c]["difficulty"] else 0) * self.takes_course_in_sem[c, s] for c in self.course_indices)
            )
        
        # minimize maximum difficulty across semesters
        model.AddMaxEquality(self.max_difficulty, self.list_difficulties)
        model.Minimize(self.max_difficulty)
        
    def dont_take_cross_listed_twice(self) -> None:
         """enforce cross-listing across courses"""
         model = self.model

         for c, course in enumerate(self.all_courses):
            crosslistings = course["crosslistings"]

            # get all crosslisted courses indices
            cross_listing_indices = [
                self.course_id_to_index.get(crosslisting)
                for crosslisting in crosslistings
                if self.course_id_to_index.get(crosslisting) is not None
            ]

            for cross_listed_course in cross_listing_indices:
                model.AddImplication(
                    self.takes_course[c], 
                    self.takes_course[cross_listed_course])

            # for s in self.semester_indices:
            #     for cross_listed_course in cross_listing_indices:
            #         model.AddImplication(self.takes_course_in_sem[c, s], self.takes_course_by_sem[cross_listed_course, s].Not())

            
                 

