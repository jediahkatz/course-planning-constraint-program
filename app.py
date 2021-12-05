from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)


@app.route('/')
def home():
    return "hello"

@app.route('/recommendations')
def recommendations():
    # TODO: call solver on template

    return render_template("rec.html")


if __name__ == '__main__':
    app.run(debug=True)

