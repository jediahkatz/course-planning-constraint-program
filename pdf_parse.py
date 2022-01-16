# Import libraries
from PIL import Image
import pytesseract
import sys
from pdf2image import convert_from_path
import os
import json

# Path of the pdf
PDF_FILE = "Akshit_Sharma_Transcript.pdf"
COURSES_JSON = "course_infos.json"
'''
Part #1 : Converting PDF to images
'''

def convert_to_images(save_to: str, pdf_file):
    pages = convert_from_path(pdf_file, 500)
    image_counter = 1

    # create directory or clear it
    if os.path.exists(save_to):
        for file in os.listdir(save_to):
            os.remove(os.path.join(save_to, file))
    else:
        os.mkdir(save_to)
    
    # Iterate through all the pages stored above
    for page in pages:

        # save filename as image
        filename = f'{save_to}page_{str(image_counter)}.jpg'
        page.save(filename, 'JPEG')
        image_counter += 1
    
    return image_counter
  
'''
Part #2 - Recognizing text from the images using OCR
'''

def write_output_txt(total_images: int, img_file_path: str):
    total_files = total_images - 1 
    
    # create text file to write the output transcript
    outfile = "transcript.txt"
    return outfile
    if os.path.exists(outfile):
        os.remove(outfile)
  
    # open file in append mode
    f = open(outfile, "a")
    
    for i in range(1, total_files + 1):

        # get filename
        filename = f'{img_file_path}page_{str(i)}.jpg'
            
        # Recognize the text as string in image using pytesseract
        text = str(((pytesseract.image_to_string(Image.open(filename)))))

        f.write(text)
    
    # Close the file after writing all the text.
    f.close()

    
    return outfile

'''
Part #3 - getting completed courses as list from transcript.txt
'''

def get_completed_courses(filename: str):
    completed = []
    semester = (0, 0)
    semesters = set()

    # load json
    json_file = open(COURSES_JSON)
    course_ids = set(course['id'] for course in json.load(json_file))

    with open(filename, 'r', encoding='UTF-8') as f:
        for line in f:
            line_split = line.strip().split(" ")

            # check if we are at beginning of section or have a course we want to add
            if line_split[0].lower() in ['fall', 'spring']:
                semester = (int(line_split[1]), 0 if line_split[0].lower() == "spring" else 1)
                semesters.add(semester)
            elif (line_split[0].lower() == "advanced" and line_split[1].lower() == 'placement') or line_split[0].lower() == "summer":
                semester = (0, 0)
                semesters.add(semester)
            else:
                # TODO: get masterlist of all courses at Penn (right now -> only works with curr semester from API)
                if len(line_split) >= 2:
                    course_name = f'{line_split[0]}-{line_split[1]}'
                    if course_name in course_ids:
                        completed.append((course_name, semester))
    
    semester_to_idx = {
        sem: i
        for i, sem in enumerate(sorted(semesters))
    }
    completed_with_idx = [
        (course_name, semester_to_idx[sem]) for course_name, sem in completed
    ]
    return completed_with_idx

if __name__ == "__main__":
    total_images = convert_to_images(save_to="./img/", pdf_file=PDF_FILE)
    outfile = write_output_txt(total_images=total_images, img_file_path="./img/")
    print(get_completed_courses(outfile))