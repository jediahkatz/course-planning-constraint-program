from flask import Flask, redirect, url_for, render_template, request, jsonify

from cp2_types import CourseRequest, CompletedClasses, Index, CourseInfo, Requirement, RequirementBlock, ScheduleParams
from fetch_data import fetch_course_infos
from solver import generate_schedule
from pdf_parse import convert_to_images, write_output_txt, get_completed_courses

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/all-courses', methods=['GET'])
def all_courses():
    all_courses_info = fetch_course_infos()
    all_course_ids = [
        course_info["id"] for course_info in all_courses_info]
    return jsonify(all_course_ids)


@app.route('//compute-schedule', methods=['POST'])
def compute_schedule():
    data = dict(request.form)
    print(data)

    return jsonify({"result": "success"})


@ app.route('/recommendations')
def recommendations():
    # TODO: call solver on template

    return render_template("rec.html")


if __name__ == '__main__':
    app.run(debug=True)
