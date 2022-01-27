from cp2_types import BaseRequirement, Requirement, RequirementBlock

# 40 CU CIS BSE
CIS_BSE: RequirementBlock = [
    # === ENGINEERING ===
    Requirement.base(courses=['CIS-110']),
    Requirement.base(courses=['CIS-120']),
    Requirement.base(courses=['CIS-121']),
    Requirement.base(courses=['CIS-240']),
    Requirement.base(courses=['CIS-262']),
    Requirement.base(courses=['CIS-320']),
    Requirement.base(courses=['CIS-380']),
    Requirement.base(courses=['CIS-400', 'CIS-410']),
    Requirement.base(courses=['CIS-401', 'CIS-411']),
    Requirement.base(courses=['CIS-471']),
    # cis electives
    *([Requirement.base(
        categories=['ENG@SEAS'], 
        depts=['CIS', 'NETS'], 
        min_number=200,
        max_number=699,
        nickname="CIS Elective"
    ) for _ in range(4)]),
    # === MATH ===
    Requirement.base(courses=['MATH-104']),
    Requirement.base(courses=['MATH-114']),
    Requirement.base(courses=['CIS-160']),
    Requirement.base(courses=['CIS-261', 'ESE-301', 'ENM-321', 'STAT-430']),
    # Requirement(courses=['MATH-240', 'MATH-312', 'MATH-313', 'MATH-314']),
    *([Requirement.base(categories=['MATH@SEAS']) for _ in range(2)]),
    # === NATURAL SCIENCE ===
    Requirement.base(courses=['PHYS-150', 'PHYS-170', 'MEAM-110']),
    Requirement.base(courses=['PHYS-151', 'PHYS-171', 'ESE-112']),
    Requirement.base(categories=['NATSCI@SEAS']),
    # # === TODO: TECHNICAL ELECTIVES ===
    *([Requirement.base(categories=['ENG@SEAS']) for _ in range(2)]),
    *([Requirement.base(categories=['ENG@SEAS', 'MATH@SEAS', 'NATSCI@SEAS']) for _ in range(4)]),
    # === GENERAL ELECTIVES ===
    Requirement.base(courses=['EAS-203']),
    *([Requirement.base(categories=['SS@SEAS', 'H@SEAS']) for _ in range(4)]),
    *([Requirement.base(categories=['SS@SEAS', 'H@SEAS', 'TBS@SEAS']) for _ in range(2)]),
    # === FREE ELECTIVES ===
    Requirement.base(categories=['SS@SEAS', 'H@SEAS'], nickname='Free Elective'),
    Requirement.base(categories=['SS@SEAS', 'H@SEAS'], nickname='Free Elective'),
    Requirement.base(categories=['SS@SEAS', 'H@SEAS'], nickname='Free Elective'),
]
SEAS_DEPTH: RequirementBlock = [
    # TODO need a way to require two from same dept...
]
SEAS_WRIT: RequirementBlock = [
    Requirement.base(depts=['WRIT'], max_number=99)
]
CIS_MSE: RequirementBlock = [
    # === CORE COURSES ===
    # theory course
    Requirement.base(courses=['CIS-502', 'CIS-511', 'CIS-677'], nickname='Theory'),
    # systems course or 501
    Requirement.base(
        courses=['CIS-501', 'CIS-505', 'CIS-548', 'CIS-553', 'CIS-555'],
        nickname='Systems'
    ),
    # core course that can be ML
    Requirement.base(courses=[
        'CIS-502', 'CIS-511',
        'CIS-505', 'CIS-548', 'CIS-553', 'CIS-555',
        'CIS-520', 'CIS-519', 'CIS-521',
        'CIS-500', 'CIS-501',
    ], nickname='Core'),
    # core course that can't be ML
    Requirement.base(courses=[
        'CIS-502', 'CIS-511',
        'CIS-505', 'CIS-548', 'CIS-553', 'CIS-555',
        'CIS-500', 'CIS-501',
    ], nickname='Core'),
    # === CIS ELECTIVES ===
    *([Requirement.base(
        depts=['CIS'], min_number=500, max_number=699,
        nickname='Grad CIS'
    ) for _ in range(2)]),
    Requirement.base(depts=['CIS'], min_number=500, max_number=700),
    # === CIS OR NON-CIS ELECTIVES ===
    # TODO: revisit this after allowing OR of requirements
    *([Requirement.base(
        categories=['ENG@SEAS', 'MATH@SEAS'], min_number=500, max_number=699,
        nickname='Grad Non-CIS'
    ) for _ in range(3)]),
]
MATH_MINOR: RequirementBlock = [
    Requirement.base(courses=['MATH-104']),
    Requirement.base(courses=['MATH-114', 'MATH-115', 'MATH-116']),
    Requirement.base(courses=['MATH-240', 'MATH-260']),
    Requirement.base(courses=['MATH-312', 'MATH-312', 'MATH-314', 'MATH-350', 'MATH-370', 'MATH-502']),
    *([Requirement.base(depts=['MATH'], min_number=202) for _ in range(2)])
]
# STAT_MINOR: RequirementBlock = [
#     Requirement(courses=['MATH-114', 'MATH-115']),
#     Requirement(courses=['MATH-114', 'MATH-115']),
# ]