## BINARIES

### cp2.py
This is the main module. Right now, it has the CIS BSE and CIS MSE requirements hard-coded.
You can run it with `python3.9 cp2.py` (I don't think it will work with lower versions).

### test_solver.py
This module contains unit tests for the constraint program and solver. There is lots of
untested behavior, but this is a decent baseline.

You can run it with `pytest` or `pytest -k substr`. The latter command only runs tests whose
name contains `substr`.

## LIBRARIES

### cp2_types.py
This library exposes all the custom types for the codebase. This code is fully typed;
**please keep it that way**! Typing is a great advantage that prevents all sorts of
easily-overlooked bugs. To take advantage of it, change your linter to `mypy` in VS Code
(`View` > `Command Palette` > `Python: Select Linter` > `mypy`).

### fetch_data.py
This library exposes the function `fetch_course_infos() -> list[CourseInfo]`, which queries
Penn Labs' Penn Courses API to get info for all courses in the current (upcoming) semester.

Unfortunately, right now I don't know a better way to do this than by making an individual
request for every course, which is slow. To speed this up, it makes the requests in parallel
in a pool of 20 threads, and then stores the results in a file called `course_infos.txt`.

**DO NOT interrupt the program while it is making API calls**, or else you will need to
delete the `course_infos.txt` file and start again from scratch. Also, unfortunately,
the data for requirements and prerequisites is not perfect, so you may need to manually
edit the file sometimes.

### solver.py
This is the largest module that contains the meat of the program. It exposes the function

```
generate_schedule(
    all_courses: list[CourseInfo],
    course_requests: list[CourseRequest],
    schedule_params: ScheduleParams,
    verbose: bool = False,
) -> Optional[tuple[Schedule, dict[Id, list[tuple[Index, Index]]]]]
```

which accepts a list of info on all courses that exist; a list of the user's requests
to take a specific course in a specific schedule, and a `ScheduleParams` object that
stores the user's curriculum requirements and additional preferences. 

The function outputs `None` if no schedule can be generated subject to the user's constraints.
Otherwise, it returns a `Schedule` and a dictionary that maps the `Id` of each course taken
to a list of the requirements that course satisfies. The list elements take the form `(b, r)`,
which means that the course satisfies `requirement_blocks[b][r]`.

The `ScheduleGenerator` class wraps the OR-Tools `CpModel` and `CpSolver`, so this is where
most of the magic happens. Most of the class functions add constraints to the model, and
in `__init__` there is a list of all the constraints that will be applied in order.
**When you add a constraint, don't forget to add it to the list!**

## DOCUMENTATION

I have tried to include a good number of comments in the code. In addition, this
file documents the organization of the codebase, and there are a couple other files:

### roadmap.txt
I have used this file to keep track of which features I would like to work on and which
ones I have already completed.

### planning.txt
Sometimes I will jot down some thoughts in this file if I need to plan out how a feature
will work.