## Project Overview

We focused on expanding functionality of the base solver and creating a balanced semester plan
based on number of courses, course workload, and prior courses taken. Specifically, features that 
we implemented include:

* Complex prereq parsing
* Parsing existing courses (from pdf) and using them in the solver
* Balanced difficulty across semesters
* taking free electives (denoted as FREE)
* disallowing cross-listed courses

We also created a basic application of the solver in the form of a web app using Flask and HTML/CSS. 

A big thanks goes out to Jediah for guiding us through this project and providing us a lot of great functionality out of the box. Contributing to the existing codebase felt really easy and intuitive and we hope that this can actually be used someday!


## File Overview
Head over to ARCHITECTURE.MD for a breakdown of what each file does.

## Installation and Usage

### Project Dependencies and Installation
This project is dependent on the following packages/system configs:

* Python-3.9
* requests
* ortools
* Pillow
* pytesseract
* pdf2image
* Flask

Now, select your appropriate poetry virtual environment (use python3.9) by running `poetry env use python3.9`. NOTE: there is a bug with poetry that I ran into if you have multiple python versions installed. To verify that the correct version of python is installed, run `poetry env info` and verify that the python version is `3.9.0`. If it isn't, because poetry caches old virtual environments, you may have to delete the appropriate cached environment by running `poetry env list` and running `poetry env remove <virtualenvname>` and running `poetry env use python3.9` again.

Now, if you run `poetry install` in your terminal in the root directory, all of the venv-related packages will be installed. 

However, in order for pdf parsing to work, you will also need `tesseract-ocr` and `poppler` which are system packages. I downloaded both using `homebrew` but in case you are on Windows, instructions for downloading `tesseract-ocr` can be found [here](https://github.com/UB-Mannheim/tesseract/wiki#tesseract-installer-for-windows). Poppler installation on Windows is a bit more difficult, but the steps are laid out in this stackoverflow [answer](https://stackoverflow.com/a/53960829).

If you are using Ubuntu, you should be able to download `tesseract-ocr` and `poppler` by running the following commands: 
* `sudo apt-get install tesseract-ocr-all`
* `sudo apt-get install poppler-utils`

### Usage
To run the web app, run `poetry run flask run` in your terminal in the root directory after downloading all required packages. Your terminal should show the local address of the web app that you can navigate to and then you can poke around the app!

In order to get a valid pdf of your transcript, navigate to your PenninTouch and go to the page that says "Transcript and GPA". Save this page as a pdf by hitting `cmnd P` or `ctrl P`. 

To run the base solver and view output on your terminal, you can replace variables in `CP2.py` to accomodate your preferences (like CourseRequests). In order to poke around with different pdf files locally, you can just upload your transcript to the root directory and change `PDF_FILE` in `CP2.py` to the path of your pdf in your local directory. You can run `CP2.py` in the same way as before, by just running `poetry run python3.9 cp2.py`.