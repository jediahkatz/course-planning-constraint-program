## in-progress:
- write tests

## todo:
- optimize model to speed up solving time
- account for timeslots in current semester
- use requirements based on CUs instead of just number of courses
    - this will break some assumptions
        - e.g. that a requirement can only be satisfied by one course
    - will also need to fetch old data for courses that aren't currently offered
        - ideally instead we can maintain a new database of CUs per course
- change course requests to more general semester requirements (can maybe keep course requests api)
- allow OR of requirements
- handle summer classes
- fix transcript parsing to be more robust
- logging
- refactor so that indices are only internal to solver (never in input)
    - basically just give uuids to requirement blocks

## done (reverse chrono):
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