from flask import Flask, redirect, url_for, render_template, request, jsonify, session
import os
from werkzeug.utils import secure_filename  
import json

from typing import Optional
from cp2_types import CourseRequest, CompletedClasses, Index, Requirement, RequirementBlock, ScheduleParams, Schedule
from fetch_data import fetch_course_infos
from solver import generate_schedule
from pdf_parse import convert_to_images, write_output_txt, get_completed_courses

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = app.root_path + '/uploads/'
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

# constant for uploading files
SAVE_TO = "./img/"

# fetch courses initially
all_courses_info = fetch_course_infos()

# add 3 free elective wild character courses (since each course can only be taken once)
for i in range(1, 4):
    all_courses_info.append({
        "id": f'FREE-{i}',
        "title": "Free Elective 1",
        "semester": "2022C",
        "prerequisites": [],
        "course_quality": None,
        "instructor_quality": None,
        "difficulty": None,
        "work_required": None,
        "crosslistings": [],
        "requirements": [],
        "sections": []
    })

# all requirement blocks
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
    # === MATH AND NATURAL SCIENCE ===
    Requirement(courses=['MATH-104']),
    Requirement(courses=['MATH-114']),
    Requirement(courses=['CIS-160']),
    Requirement(courses=['CIS-261', 'ESE-301', 'ENM-321', 'STAT-430']),
    Requirement(courses=['MATH-240', 'MATH-312', 'MATH-313', 'MATH-314']),
    Requirement(courses=['PHYS-150', 'PHYS-170', 'MEAM-110']),
    Requirement(courses=['PHYS-151', 'PHYS-171', 'ESE-112']),
    Requirement(categories=['MATH@SEAS', 'NATSCI@SEAS']),
    # # === TODO: TECHNICAL ELECTIVES ===
    *([Requirement(categories=['ENG@SEAS'])] * 6),
    # # # === GENERAL ELECTIVES ===
    Requirement(courses=['EAS-203']),
    *([Requirement(categories=['SS@SEAS', 'H@SEAS'])] * 4),
    *([Requirement(categories=['SS@SEAS', 'H@SEAS', 'TBS@SEAS'])] * 2),
    # # # === TODO: FREE ELECTIVE ===
    Requirement(depts=['FREE'], nickname='Free Elective'),
    Requirement(depts=['FREE'], nickname='Free Elective'),
    Requirement(depts=['FREE'], nickname='Free Elective'),
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
        categories=['ENG@SEAS'], min_number=500, max_number=699,
        nickname='Grad Non-CIS'
    )] * 3),
]

ALL_REQUIREMENT_BLOCKS: list[RequirementBlock] = [
    CIS_BSE,
    CIS_MSE,
    SEAS_WRIT,
]
block_idx = lambda block: {tuple(block): b for b, block in enumerate(ALL_REQUIREMENT_BLOCKS)}[tuple(block)]
MAX_DOUBLE_COUNTING: dict[tuple[Index, Index], Optional[int]] = {
    (block_idx(CIS_BSE), block_idx(CIS_MSE)): 3,
    (block_idx(CIS_BSE), block_idx(SEAS_WRIT)): None,
    (block_idx(CIS_MSE), block_idx(SEAS_WRIT)): 0
}

MIN_COURSES_PER_SEMESTER = 4

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/all-courses', methods=['GET'])
def all_courses():
    all_course_ids = [course_info["id"] for course_info in all_courses_info]
    return jsonify(all_course_ids)


@app.route('/compute-schedule', methods=['GET', 'POST'])
def compute_schedule():
    response = dict(request.form)

    completed_courses = []

    # if we have the transcript as well
    if response["proceed_wo_transcript"] == 'false':
        # save transcript file 
        file = request.files["transcript"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            # if path exists, remove existing pdf files
            if os.path.exists(app.config["UPLOAD_FOLDER"]):
                 for existing_file in os.listdir(app.config["UPLOAD_FOLDER"]):
                     os.remove(os.path.join(app.config["UPLOAD_FOLDER"], existing_file))
            else:
                os.mkdir(app.config["UPLOAD_FOLDER"])

            file.save(path)

            # get list of completed courses using OCR recognition
            total_images = convert_to_images(save_to=SAVE_TO, pdf_file=path)
            outfile = write_output_txt(total_images=total_images, img_file_path=SAVE_TO)
            completed_courses = get_completed_courses(outfile)
            
    # run solver
    completed, course_requests, all_courses = get_solver_params(json.loads(response['requested_courses']), completed_courses)
    all_requirement_blocks, max_double_counting = get_requirement_blocks(False if response["MSE"] == "false" else True) 

    params = ScheduleParams(
        int(response["numSemesters"]),
        int(response["numCourses"]),
        MIN_COURSES_PER_SEMESTER,
        all_requirement_blocks,
        max_double_counting
    )

    course_schedule = generate_schedule(all_courses, course_requests, completed, params, verbose=True)

    # assign sessions variable
    session["recommended_courses"] = course_schedule[0]

    return jsonify(dict(redirect=url_for('recommendations')))

def get_requirement_blocks(is_submatriculating):
    if is_submatriculating:
        all_requirement_blocks = [CIS_BSE, CIS_MSE, SEAS_WRIT]
        block_idx = lambda block: {tuple(block): b for b, block in enumerate(all_requirement_blocks)}[tuple(block)]
        max_double_counting: dict[tuple[Index, Index], Optional[int]] = {
            (block_idx(CIS_BSE), block_idx(CIS_MSE)): 3,
            (block_idx(CIS_BSE), block_idx(SEAS_WRIT)): None,
            (block_idx(CIS_MSE), block_idx(SEAS_WRIT)): 0
        }
    else:
        all_requirement_blocks = [CIS_BSE, SEAS_WRIT]
        block_idx = lambda block: {tuple(block): b for b, block in enumerate(all_requirement_blocks)}[tuple(block)]
        max_double_counting: dict[tuple[Index, Index], Optional[int]] = {
            (block_idx(CIS_BSE), block_idx(SEAS_WRIT)): None,
        }
    
    return all_requirement_blocks, max_double_counting



def get_solver_params(requested_courses, completed_courses):
    # convert completed courses into proper class
    completed: list[CompletedClasses] = [CompletedClasses(element[0], element[1]) for element in completed_courses]   
    completed_course_ids = set(course_id for course_id, _ in completed)

    course_requests: list[CourseRequest] = [
        CourseRequest(course["course"], int(course["semester"])) for course in requested_courses
    ]
    request_ids = set(course_id for course_id, _ in course_requests)

    # get all_courses
    all_courses = [
        course for course in all_courses_info
        if course['id'] in completed_course_ids.union(request_ids) or any(
            req.satisfied_by_course(course)
            for major in ALL_REQUIREMENT_BLOCKS
            for req in major
        )
    ]
    return completed, course_requests, all_courses

@app.route('/recommendations')
def recommendations():
    # display results
    semesters = range(len(session["recommended_courses"]))

    return render_template("rec.html", data=session["recommended_courses"], semesters=semesters)


if __name__ == '__main__':
    app.run(debug=True)
