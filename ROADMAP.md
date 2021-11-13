in-progress:
- write tests

todo:
- optimize model to speed up solving time
- account for timeslots in current semester
- product decisions: how will users actually use this?
    - plan out an entire 4 year curriculum? probably not
    - plan out the coming semester? highly likely
    - plan out all remaining semesters? decent likely, not entirely possible but can be approximated
        - with new block schedule, maybe things get a bit more consistent in terms of course timeslots
- enforce complex prerequisites (e.g. ECON 001 AND (STAT 101 OR STAT 102))
- user can request to take class in any semester
- handle courses only offered in fall/spring
- change course requests to more general semester requirements (can maybe keep course requests api)
- parse transcripts to get course history (obviously do not read grades)
- logging

done (reverse chrono):
- create a better system for double counting (+ reqs that can always double count)
- big refactor + types
- requirements can have nicknames
- enforce basic prerequisites (e.g. CIS 120, 160)
- limit on double counting
- user can request to take class in specified semester
- parallelize API requests
- cache API requests (to a local file)
