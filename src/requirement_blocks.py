from cp2_types import Requirement, RequirementBlock

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
        allow_partial_cu=True,
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
    *([Requirement.base(
        categories=['ENG@SEAS', 'MATH@SEAS', 'NATSCI@SEAS'],
        allow_partial_cu=True,
    ) for _ in range(4)]),
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
# how to implement "waived" requirements...?
# DATS_MSE: RequirementBlock = [
#     Requirement.base(courses=[])
# ]
################################
#########   M A J O R S
################################

DSGN_MAJOR: RequirementBlock = [
    Requirement.base(courses=['DSGN-264']),
    Requirement.base(courses=['DSGN-306']),
    *([
        Requirement.base(
            nickname="Interactive Design Studio",
            courses=['DSGN-266', 'DSGN-268', 'DSGN-317', 'DSGN-328', 'DSGN-337', 'DSGN-378'], 
        )
        for _ in range(4)
    ]),
    Requirement.base(nickname='Art History', courses=['ARTH-101', 'ARTH-102', 'ARTH-106', 'ARTH-300'])
    *([
        Requirement.base(nickname='Art Theory', courses=['ARCH-411', 'DSGN-300', 'DSGN-343', 'URBS-205', 'VLST-101'])
        for _ in range(3)
    ]),
    Requirement.base(courses=['DSGN-488']),
    Requirement.base(courses=['DSGN-489']),
    *([
        Requirement.base(nickname='Art/Design Elective', depts=['FNAR', 'DSGN'])
    ])
]

################################
#########   M I N O R S
################################

MATH_MINOR: RequirementBlock = [
    Requirement.base(courses=['MATH-104']),
    Requirement.base(courses=['MATH-114', 'MATH-115', 'MATH-116']),
    Requirement.base(courses=['MATH-240', 'MATH-260']),
    Requirement.base(courses=['MATH-312', 'MATH-312', 'MATH-314', 'MATH-350', 'MATH-370', 'MATH-502']),
    *([Requirement.base(depts=['MATH'], min_number=202) for _ in range(2)])
]
_STAT_ELECTIVE_COURSES = [
    'STAT-405', 'STAT-410', 'STAT-422', 'STAT-432', 'STAT-433', 'STAT-435',
    'STAT-535', 'STAT-711', 'STAT-442', 'STAT-470', 'STAT-503', 'STAT-471',
    'STAT-571', 'STAT-474', 'STAT-974', 'STAT-475', 'STAT-476', 'STAT-477',
    'STAT-481', 'STAT-581', 'STAT-490', 'STAT-590', 'STAT-515', 'STAT-520',
    'STAT-521', 'STAT-531', 'STAT-542', 'STAT-930', 'STAT-931', 'STAT-961',
    'ECON-221', 'ECON-222', 'ECON-244', 'MKTG-309', 'MKTG-809', 'OIDD-930',
    'CIS-545'
]
STAT_MINOR: RequirementBlock = [
    Requirement.base(courses=['MATH-114', 'MATH-115']),
    Requirement.any([
        # Introductory sequence of STAT 430-431 + 4 electives
        Requirement.all([
            Requirement.base(courses=['STAT-430']),
            Requirement.base(courses=['STAT-431']),
            *([
                Requirement.base(courses=_STAT_ELECTIVE_COURSES, nickname='STAT') 
                for _ in range(4)
            ])
        ]),
        # Other introductory sequence + STAT 430 + 3 electives
        Requirement.all([
            Requirement.base(courses=['STAT-430']),
            Requirement.any([
                Requirement.all([
                    Requirement.base(courses=['STAT-101']),
                    Requirement.base(courses=['STAT-102']),
                ]),
                Requirement.all([
                    Requirement.base(courses=['STAT-111']),
                    Requirement.base(courses=['STAT-112']),
                ]),
            ]),
            *([
                Requirement.base(courses=_STAT_ELECTIVE_COURSES, nickname='STAT') 
                for _ in range(3)
            ])
        ]),
    ])
]
_DATS_MINOR_CATEGORIES = [
    # Data-Centric Programming
    ['CIS-105', 'ENGR-105', 'OIDD-311', 'STAT-405', 'STAT-470', 'ESE-305'],
    # Statistics
    ['EAS-205', 'CIS-261', 'ESE-301', 'BIOL-446', 'STAT-430', 'STAT-476'],
    # Data Pipeline
    ['CIS-455', 'CIS-555', 'CIS-450', 'CIS-550', 'NETS-213', 'OIDD-105', 'STAT-475'],
    # Data Analysis
    [
        'CIS-419', 'CIS-519', 'CIS-421', 'CIS-520', 'MKTG-309', 'OIDD-410',
        'STAT-422', 'STAT-435', 'STAT-471', 'STAT-474', 'STAT-520'
    ],
    # Modeling
    ['NETS-312', 'MKTG-271', 'OIDD-325', 'OIDD-353', 'STAT-433', 'STAT-436']
]
DATS_MINOR: RequirementBlock = [
    Requirement.base(courses=['CIS-120']),
    Requirement.base(courses=['CIS-419', 'CIS-519', 'CIS-520', 'STAT-471']),
    Requirement.base(courses=['CIS-545', 'NETS-212']),
    Requirement.base(courses=['ENM-321', 'ESE-402', 'STAT-431']),
    Requirement(
        min_satisfied_reqs=2,
        min_credits=2,
        multi_requirements=[
            Requirement.base(
                courses=_DATS_MINOR_CATEGORIES[0], 
                nickname="Data-Centric Programming"
            ),
            Requirement.base(
                courses=_DATS_MINOR_CATEGORIES[1],
                nickname="Statistics"
            ),
            Requirement.base(
                courses=_DATS_MINOR_CATEGORIES[2], 
                nickname="Data Pipeline"
            ),
            Requirement.base(
                courses=_DATS_MINOR_CATEGORIES[3], 
                nickname="Data Analysis"
            ),
            Requirement.base(
                courses=_DATS_MINOR_CATEGORIES[4], 
                nickname="Modeling"
            ),
        ]
    )
]
COGS_MINOR: RequirementBlock = [
    Requirement.base(courses=['COGS-001', 'CIS-140', 'LING-105', 'PHIL-044', 'PSYC-107']),
    
]
_ECON_ELECTIVE_COURSES = [
    'ECON-103', 'ECON-104', 'ECON-221', 'ECON-222', 'ECON-14',
    'ECON-030', 'ECON-033', 'ECON-035', 'ECON-036', 'ECON-039', 
    'ECON-231', 'ECON-232', 'ECON-233', 'ECON-234', 'ECON-235',
    'ECON-236', 'ECON-237', 'ECON-013', 'ECON-211', 'ECON-212',
    'ECON-245', 'ECON-260', 'ECON-262', 'ECON-102', 'ECON-210',
    'ECON-241', 'ECON-242', 'ECON-243', 'ECON-246', 'ECON-244',
    'ECON-024', 'ECON-050', 'ECON-251', 'ECON-252', 'ECON-262',
]
ECON_MINOR: RequirementBlock = [
    Requirement.base(courses=['ECON-001']),
    Requirement.base(courses=['ECON-002']),
    Requirement.base(courses=['ECON-101']),
    Requirement.base(
        courses=_ECON_ELECTIVE_COURSES,
        min_number=200,    
    ),
    Requirement.base(courses=_ECON_ELECTIVE_COURSES),
    Requirement.base(courses=_ECON_ELECTIVE_COURSES),
]
ENGL_MINOR: RequirementBlock = [
    Requirement.base(courses=['ENGL-020', 'ENGL-040']),
    Requirement.elective(depts=['ENGL'], min_number=200),
    Requirement.elective(depts=['ENGL']),
    Requirement.elective(depts=['ENGL']),
    Requirement.elective(depts=['ENGL']),
    Requirement.elective(depts=['ENGL']),
]
SOCI_MINOR: RequirementBlock = [
    Requirement.base(courses=['SOCI-001']),
    Requirement.base(courses=['SOCI-100']),
    Requirement.base(courses=['SOCI-125', 'SOCI-126']),
    Requirement.elective(depts=['SOCI']),
]