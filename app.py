from flask import Flask, redirect, url_for, render_template, request, jsonify

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/all-courses', methods=['GET'])
def all_courses():
    print("got request")
    return jsonify(["Course 1", "Course 2", "Course 3"])


@ app.route('/recommendations')
def recommendations():
    # TODO: call solver on template

    return render_template("rec.html")


if __name__ == '__main__':
    app.run(debug=True)
