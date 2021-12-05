""" Valid : AND of ORs """
# - (BIOL 483 OR BIOL 493) AND GCB 534 AND (GCB 535 OR GCB 536)
# - BIOL 421 OR BIOL 526 OR BIOL 527 OR BIOL 528 OR BIOL 540
# - SPAN 219 or SPAN 223
# - (STAT 613 OR STAT 621) OR STAT 102

""" Invalid """
# - MGEC 611 AND MGEC 612 OR (ECON 701 AND ECON 703) -> MIXED
# - BIBB 109 AND (BIOL 101 OR BIOL 102) OR (BIOL 123 OR BIOL 124) -> MIXED
# - (STAT 613 OR STAT 621) OR STAT 102
# - CIS 121, CIT 594, or equivalent, or permission of the instructor
# - MATH 241, PHYS 141 OR 151, ENGR 105
# - ESE 500, 504 or 605
# - (BIOL 101 AND BIOL 102) OR BIOL 121  -> TODO: could expand it to (BIOL 101 OR BIOL 121) AND (BIOL 102 OR BIOL 121)

from typing import cast
from cp2_types import CourseInfo

""" Returns AND, OR, MIXED, or NONE """
def get_top_level_operator(prereq_string: str) -> str:
    current_top_level = "NONE"
    open_bracket_count = 0
    parts = prereq_string.upper().split(' ')
    for part in parts:
        if part == '(':
            open_bracket_count += 1
        elif part == ')':
            open_bracket_count -= 1
        elif part in ['AND', 'OR']:
            if open_bracket_count == 0:
                if part != current_top_level and current_top_level != "NONE":
                    current_top_level = "MIXED"
                    break
                current_top_level = part
    return current_top_level

""" Returns 'DEPT 123' -> [DEPT-123] and '(DEPT 123 OR DEPT 456)' -> [DEPT-123, DEPT-456]"""
def get_individual_prereq(prereq_string: str) -> list[str]:
    if 'AND' in prereq_string:
        # 3-level operator not supported
        return None
    prereq_string = prereq_string.replace('(', '').replace(')', '')
    individual_prereq = []
    parts = prereq_string.split(' OR ')
    for part in parts:
        dept_code = part.split(' ')
        if len(dept_code) != 2:
            # Ill-formatted
            return None
        individual_prereq.append(f'{dept_code[0]}-{dept_code[1]}')
    return individual_prereq

""" 
    Course prereqs returned as an 2D-array: [[Dept-123, Dept-456], [Dept-789]]
    interpreted as: (Dept-123 OR Dept-456) AND Dept-789               
"""
def parse_prerequisites(all_courses: list[dict]) -> list[CourseInfo]:
    for course in all_courses:
        prereqs_string: str = course['prerequisites']
        top_level_operator = get_top_level_operator(prereqs_string)
        
        if top_level_operator == "NONE":
            # Expecting format: Dept 123, 456, 789
            parts = prereqs_string.split(', ')
            first_course = parts[0].split(' ')
            if len(first_course) != 2:
                # Ill-formatted
                course['prerequisites'] = []
                continue
            dept, code = first_course
            codes = [code] + parts[1:]
            if dept != dept.strip() or any(code != code.strip() for code in codes):
                # Ill-formatted
                course['prerequisites'] = []
                continue
            
            course['prerequisites'] = [[f'{dept}-{code}'] for code in codes]
        
        elif top_level_operator == "MIXED":
            ## Ill-formatted
            course['prerequisites'] = []
            continue
        
        else:
            # Expecting AND of ORs: (DEPT 123 OR DEPT 456) AND DEPT 789
            new_prereq_list = []
            list_of_and_prereqs = prereqs_string.split(' AND ')
            for and_prereq in list_of_and_prereqs:
                individual_prereq = get_individual_prereq(and_prereq)
                if individual_prereq is None:
                    # Ill-formatted
                    course['prerequisites'] = []
                    continue
                new_prereq_list.append(individual_prereq)
            course['prerequisites'] = new_prereq_list
    
    return cast(list[CourseInfo], all_courses)

s = '(STAT 613 OR STAT 621) OR STAT 102'
print(get_top_level_operator(s))
print(get_individual_prereq(s))