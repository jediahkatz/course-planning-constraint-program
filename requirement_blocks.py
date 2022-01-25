from cp2_types import Requirement, RequirementBlock

# 40 CU CIS BSE
CIS_BSE: RequirementBlock = [
    # === ENGINEERING ===
    Requirement(courses=['CIS-110']),
    Requirement(courses=['CIS-120']),
    Requirement(courses=['CIS-121']),
    Requirement(courses=['CIS-240']),
    Requirement(courses=['CIS-262']),
    Requirement(courses=['CIS-320']),
    Requirement(courses=['CIS-380']),
    Requirement(courses=['CIS-400', 'CIS-410']),
    Requirement(courses=['CIS-401', 'CIS-411']),
    Requirement(courses=['CIS-471']),
    # cis electives
    *([Requirement(
        categories=['ENG@SEAS'], 
        depts=['CIS', 'NETS'], 
        min_number=200,
        max_number=699,
        nickname="CIS Elective"
    )] * 4),
    # === MATH ===
    Requirement(courses=['MATH-104']),
    Requirement(courses=['MATH-114']),
    Requirement(courses=['CIS-160']),
    Requirement(courses=['CIS-261', 'ESE-301', 'ENM-321', 'STAT-430']),
    # Requirement(courses=['MATH-240', 'MATH-312', 'MATH-313', 'MATH-314']),
    *([Requirement(categories=['MATH@SEAS'])] * 2),
    # === NATURAL SCIENCE ===
    Requirement(courses=['PHYS-150', 'PHYS-170', 'MEAM-110']),
    Requirement(courses=['PHYS-151', 'PHYS-171', 'ESE-112']),
    Requirement(categories=['NATSCI@SEAS']),
    # # === TODO: TECHNICAL ELECTIVES ===
    *([Requirement(categories=['ENG@SEAS'])] * 2),
    *([Requirement(categories=['ENG@SEAS', 'MATH@SEAS', 'NATSCI@SEAS'])] * 4),
    # === GENERAL ELECTIVES ===
    Requirement(courses=['EAS-203']),
    *([Requirement(categories=['SS@SEAS', 'H@SEAS'])] * 4),
    *([Requirement(categories=['SS@SEAS', 'H@SEAS', 'TBS@SEAS'])] * 2),
    # === FREE ELECTIVES ===
    Requirement(categories=['SS@SEAS', 'H@SEAS'], nickname='Free Elective'),
    Requirement(categories=['SS@SEAS', 'H@SEAS'], nickname='Free Elective'),
    Requirement(categories=['SS@SEAS', 'H@SEAS'], nickname='Free Elective'),
]
SEAS_DEPTH: RequirementBlock = [
    # TODO need a way to require two from same dept...
]
SEAS_WRIT: RequirementBlock = [
    Requirement(depts=['WRIT'], max_number=99)
]
CIS_MSE: RequirementBlock = [
    # === CORE COURSES ===
    # theory course
    Requirement(courses=['CIS-502', 'CIS-511', 'CIS-677'], nickname='Theory'),
    # systems course or 501
    Requirement(
        courses=['CIS-501', 'CIS-505', 'CIS-548', 'CIS-553', 'CIS-555'],
        nickname='Systems'
    ),
    # core course that can be ML
    Requirement(courses=[
        'CIS-502', 'CIS-511',
        'CIS-505', 'CIS-548', 'CIS-553', 'CIS-555',
        'CIS-520', 'CIS-519', 'CIS-521',
        'CIS-500', 'CIS-501',
    ], nickname='Core'),
    # core course that can't be ML
    Requirement(courses=[
        'CIS-502', 'CIS-511',
        'CIS-505', 'CIS-548', 'CIS-553', 'CIS-555',
        'CIS-500', 'CIS-501',
    ], nickname='Core'),
    # === CIS ELECTIVES ===
    *([Requirement(
        depts=['CIS'], min_number=500, max_number=699,
        nickname='Grad CIS'
    )] * 2),
    Requirement(depts=['CIS'], min_number=500, max_number=700),
    # === CIS OR NON-CIS ELECTIVES ===
    # TODO: revisit this after allowing OR of requirements
    *([Requirement(
        categories=['ENG@SEAS', 'MATH@SEAS'], min_number=500, max_number=699,
        nickname='Grad Non-CIS'
    )] * 3),
]
MATH_MINOR: RequirementBlock = [
    Requirement(courses=['MATH-104']),
    Requirement(courses=['MATH-114', 'MATH-115', 'MATH-116']),
    Requirement(courses=['MATH-240', 'MATH-260']),
    Requirement(courses=['MATH-312', 'MATH-312', 'MATH-314', 'MATH-350', 'MATH-370', 'MATH-502']),
    *([Requirement(depts=['MATH'], min_number=202)] * 2)
]
# STAT_MINOR: RequirementBlock = [
#     Requirement(courses=['MATH-114', 'MATH-115']),
#     Requirement(courses=['MATH-114', 'MATH-115']),
# ]