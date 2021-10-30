from typing_extensions import IntVar
from ortools.sat.python import cp_model
from cp2_types import (
    CourseInfo, ScheduleParams, CourseRequest, RequirementBlock, Id, Index, VarMap1D, VarMap2D, VarMap3D
)

PRECOLLEGE_SEM: Index = 0

def generate_schedule(
    all_courses: list[CourseInfo],
    major_requirements: list[RequirementBlock],
    course_requests: list[CourseRequest],
    schedule_params: ScheduleParams,
) -> None:
    """ Attempt to generate a schedule from the inputs and print it. """
    generator = ScheduleGenerator(all_courses, major_requirements, course_requests, schedule_params)
    generator.solve()

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
    major_requirements: list[RequirementBlock]
    schedule_params: ScheduleParams
    precollege_credits: set[Id]
    course_indices: range
    semester_indices: range
    semester_indices_with_precollege: range
    major_indices: range
    
    # Model
    model: cp_model.CpModel
    num_double_counts: cp_model.IntVar
    num_courses_taken: cp_model.IntVar
    takes_course: VarMap1D
    takes_course_in_sem: VarMap2D
    takes_course_by_sem: VarMap2D
    is_satisfied: VarMap2D
    satisfies: VarMap3D

    def __init__(
        self,
        all_courses: list[CourseInfo], 
        major_requirements: list[RequirementBlock],
        course_requests: list[CourseRequest],
        schedule_params: ScheduleParams,
    ) -> None:
        print('Constructing model...')
        self.model = cp_model.CpModel()
        self.all_courses = all_courses
        self.course_id_to_index = {course_id['id']: c for c, course_id in enumerate(all_courses)}
        self.course_indices = range(len(all_courses))
        self.major_requirements = major_requirements
        self.major_indices = range(len(major_requirements))
        self.course_requests = course_requests
        self.precollege_credits = set(request.course_id for request in course_requests if request.semester == PRECOLLEGE_SEM)
        self.schedule_params = schedule_params
        self.semester_indices = range(1, schedule_params.num_semesters+1)
        self.semester_indices_with_precollege = range(schedule_params.num_semesters+1)
        self.create_cp_vars()
        constraints = [
            self.link_takes_course_vars,
            self.link_satisfies_vars,
            self.satisfy_all_requirements_once,
            self.enforce_max_courses_per_semester,
            self.enforce_max_double_counting,
            self.take_courses_at_most_once,
            self.must_take_course_to_count,
            self.courses_only_satisfy_requirements,
            self.no_double_counting_within_requirement_blocks,
            self.dont_take_unnecessary_courses,
            self.enforce_prerequisites,
            self.take_requested_courses,
            self.dont_assign_precollege_semester,
            self.too_many_courses_infeasible,
        ]
        for constraint in constraints:
            constraint()

    def solve(self) -> None:
        print('Solving model...')
        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = 8
        if solver.Solve(self.model) in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            print(f'Solution found ({solver.Value(self.num_courses_taken)} courses in {self.schedule_params.num_semesters} semesters)')
            print()
            for s in self.semester_indices:
                course_indices: list[Index] = [
                    c for c in self.course_indices
                    if solver.Value(self.takes_course_in_sem[c, s]) == 1
                ]
                course_indices_to_satisfied_major_req_indices = {
                    c: [
                        (m, i)
                        for m in self.major_indices
                        for i in range(len(self.major_requirements[m]))
                        if solver.Value(self.satisfies[c, m, i]) == 1
                    ]
                    for c in course_indices
                }

                print(f'SEMESTER {s}:')
                print('------------------')

                for c in course_indices:
                    course_id = self.all_courses[c]['id']
                    requirement_names = [
                        str(self.major_requirements[m][i])
                        for (m, i) in course_indices_to_satisfied_major_req_indices[c]
                    ]
                    requirement_names_str = ', '.join(requirement_names)
                    # Indicate double-counted courses with a star
                    maybe_star = '*' if len(requirement_names) > 1 else ''
                    print(f'+ {maybe_star}{course_id} (satisfies {requirement_names_str})')
                
                print()

        else:
            print('Not possible to generate a schedule that meets the specifications!\n')

        print(solver.ResponseStats())

    def create_cp_vars(self) -> None:
        """ Initialize all CP variables. """
        model = self.model

        # number of courses that count across more than one requirement block
        self.num_double_counts = model.NewIntVar(0, self.schedule_params.max_double_counting, '')
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
        # satisfies[c, m, i] is true iff course c satisfies requirements[i] for major m
        self.satisfies = {
            (c, m, i): model.NewBoolVar('')
            for c in self.course_indices
            for m in self.major_indices
            for i in range(len(self.major_requirements[m]))
        }
        # satisfies[m, i] is true if requirements[i] for major m is satisfied
        self.is_satisfied = {
            (m, i): model.NewBoolVar('')
            for m in self.major_indices
            for i in range(len(self.major_requirements[m]))
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
        for m in self.major_indices:
            for i in range(len(self.major_requirements[m])):
                model.AddBoolOr([
                    self.satisfies[c, m, i] for c in self.course_indices
                ]).OnlyEnforceIf(
                    self.is_satisfied[m, i]
                )
                
                model.AddBoolAnd([
                    self.satisfies[c, m, i].Not() for c in self.course_indices
                ]).OnlyEnforceIf(
                    self.is_satisfied[m, i].Not()
                )

    def satisfy_all_requirements_once(self) -> None:
        """ All requirements must be satisfied by exactly one course. """
        model = self.model
        for m in self.major_indices:
            for i in range(len(self.major_requirements[m])):
                # A requirement should be satisfied by exactly one course
                model.Add(
                    sum(self.satisfies[c, m, i] for c in self.course_indices) == 1
                )
                # Redundant: all requirements must be satisfied
                model.Add(
                    self.is_satisfied[m, i] == 1
                )
        
    def enforce_max_courses_per_semester(self) -> None:
        """ Limit the maximum number of courses per semester based on the schedule params. """
        model = self.model
        for s in self.semester_indices:
            model.Add(
                sum(self.takes_course_in_sem[c, s] for c in self.course_indices)
                <= 
                self.schedule_params.max_courses_per_semester
            )

    def enforce_max_double_counting(self) -> None:
        """ Limit the number of courses that can be double counted based on the schedule params. """
        # TODO: decide what to do about triple+ counting; right now it's disallowed
        # possible future BUG: if we allow triple counting, then need to change equation below:
        # total number of courses = total number of requirements - num_double_counts
        model = self.model

        double_count_boolvars = []
        for c in self.course_indices:
            num_times_counted = model.NewIntVar(0, 2, '')
            model.Add(
                num_times_counted == sum(
                    self.satisfies[c, m, i] 
                    for m in self.major_indices
                    for i in range(len(self.major_requirements[m]))
                )
            )
            is_double_counted = model.NewBoolVar('')
            double_count_boolvars.append(is_double_counted)
            model.Add(num_times_counted == 2).OnlyEnforceIf(is_double_counted)
            model.Add(num_times_counted < 2).OnlyEnforceIf(is_double_counted.Not())

        # note: this is just the definition of num_double_counts
        # the upper bound comes from our initialization of num_double_counts in create_cp_vars()
        model.Add(self.num_double_counts == sum(double_count_boolvars))

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
            for m in self.major_indices:
                for i in range(len(self.major_requirements[m])):
                    model.AddImplication(
                        self.takes_course[c].Not(), 
                        self.satisfies[c, m, i].Not()
                    )

    def courses_only_satisfy_requirements(self) -> None:
        """ A course cannot satisfy anything that it is not allowed to. """
        model = self.model
        for c, course in enumerate(self.all_courses):
            for m in self.major_indices:
                for i, req in enumerate(self.major_requirements[m]):
                    if not req.satisfied_by_course(course):
                        model.Add(self.satisfies[c, m, i] == 0)

    def no_double_counting_within_requirement_blocks(self) -> None:
        """ A course can only count once within a single block of requirements. """
        model = self.model
        for c in self.course_indices:
            for m in self.major_indices:
                model.Add(
                    sum(self.satisfies[c, m, i] for i in range(len(self.major_requirements[m]))) <= 1
                )

    def dont_take_unnecessary_courses(self) -> None:
        """ If a course won't satisfy any requirements, don't take it. """
        # TODO: unless we specifically requested it
        model = self.model
        for c in self.course_indices:
            course_satisfies_something = model.NewBoolVar('')
            model.AddBoolOr([
                self.satisfies[c, m, i] 
                for m in self.major_indices
                for i in range(len(self.major_requirements[m]))
            ]).OnlyEnforceIf(course_satisfies_something)
            model.AddBoolAnd([
                self.satisfies[c, m, i].Not()
                for m in self.major_indices
                for i in range(len(self.major_requirements[m]))
            ]).OnlyEnforceIf(course_satisfies_something.Not())
            model.AddImplication(course_satisfies_something.Not(), self.takes_course[c].Not())

    def enforce_prerequisites(self) -> None:
        """ If we have taken some course by sem s, we must have taken its prereqs by sem s-1. """
        # TODO: allow a mechanism for ignoring prereqs
        model = self.model
        for c, course in enumerate(self.all_courses):
            for prereq_id in course['prerequisites']:
                # Ignore prereqs that we don't have an entry for
                # TODO: log this
                if (p := self.course_id_to_index.get(prereq_id)) is not None:
                    for s in self.semester_indices:
                        model.AddImplication(
                            self.takes_course_by_sem[c, s], 
                            self.takes_course_by_sem[p, s-1]
                        )

    def take_requested_courses(self) -> None:
        """ Take the courses that the student requested. """
        model = self.model
        for course_id, sem in self.course_requests:
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
        """ Give the model some helpful facts to recognize schedules with too many courses to be feasible. """
        model = self.model
        num_semesters = self.schedule_params.num_semesters
        max_courses_per_semester  = self.schedule_params.max_courses_per_semester

        num_courses_ub = num_semesters * max_courses_per_semester + len(self.precollege_credits)
        self.num_courses_taken = model.NewIntVar(0, num_courses_ub, '')
        model.Add(
            self.num_courses_taken == sum(self.takes_course[c] for c in self.course_indices)
        )
        num_major_requirements = sum(len(major) for major in self.major_requirements)
        model.Add(
            self.num_courses_taken >= num_major_requirements - self.num_double_counts
        )