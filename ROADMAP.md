## in-progress:
- write tests

## todo:
- optimize model to speed up solving time
- account for timeslots in current semester
- product decisions: how will users actually use this?
    - plan out an entire 4 year curriculum? probably not
    - plan out the coming semester? highly likely
    - plan out all remaining semesters? decent likely, not entirely possible but can be approximated
        - with new block schedule, maybe things get a bit more consistent in terms of course timeslots
- user can request to take class in any semester
- handle courses only offered in fall/spring
- change course requests to more general semester requirements (can maybe keep course requests api)
- parse transcripts to get course history (obviously do not read grades)
- logging

## Nischal-Akshay todo:
- account for timeslots in the current semester (Nischal)
- fall vs spring classes (Nischal)
- parse transcripts to get course history (Akshay)
- clean the fetching of course info so that it can be used in the upcoming semesters (Akshay)
- user can request to take class in any semester (Akshay)
- balance workload across semsters in terms of number of courses and tech vs non-tech classes (Akshay)

## Nischal-Akshay done:
- enforce complex prerequisites (Nischal)
- wild card courses for free electives (Nischal)

## done (reverse chrono):
- enforce complex prerequisites (e.g. ECON 001 AND (STAT 101 OR STAT 102))
- create a better system for double counting (+ reqs that can always double count)
- big refactor + types
- requirements can have nicknames
- enforce basic prerequisites (e.g. CIS 120, 160)
- limit on double counting
- user can request to take class in specified semester
- parallelize API requests
- cache API requests (to a local file)
