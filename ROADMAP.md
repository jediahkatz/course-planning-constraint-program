## in-progress:
- write tests

## todo:
- optimize model to speed up solving time
    - reduce number of vars and constraints? 
        - e.g. don't even create variable satisfies[c, r] if course c can't satisfy requirement r
    - add redundant constraints?
    - cache parameter-independent parts of model so that it doesn't take so long to initialize
    - generate hints somehow based on a fast poly-time algo?
- account for timeslots in current semester
- change course requests to more general semester requirements (can maybe keep course requests api)
- handle summer classes
- fix transcript parsing to be more robust
- logging
- refactor so that indices are only internal to solver (never in input)
    - basically just give uuids to requirement blocks

## done (reverse chrono):
- make electives <= 1 CU and implement allow_partial_cu for BaseRequirements
- use requirements based on CUs instead of just number of courses
- add lower bound to quickly determine infeasiblity in problems with too many requirements
- allow requirement groups with cardinality constraints on subrequirements
- handle courses only offered in fall/spring
- user can request to take class in any semester
- allow triple counting for some requirement blocks (e.g minors)
- don't take crosslisted courses twice (Akshay/Nischal)
- differentiate requested courses from already taken courses (Akshay/Nischal)
- parse transcripts to get course history (Akshay)
- balance workload across semsters in terms of number of courses and tech vs non-tech classes (Akshay)
- enforce complex prerequisites (Nischal)
- enforce complex prerequisites (e.g. ECON 001 AND (STAT 101 OR STAT 102))
- create a better system for double counting (+ reqs that can always double count)
- big refactor + types
- requirements can have nicknames
- enforce basic prerequisites (e.g. CIS 120, 160)
- limit on double counting
- user can request to take class in specified semester
- parallelize API requests
- cache API requests (to a local file)