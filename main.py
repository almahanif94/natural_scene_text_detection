import os
from app import app
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import cv2
import pytesseract
import datefinder
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--link", help='Please enter path to tesseract.exe')
args = parser.parse_args()

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
pytesseract.pytesseract.tesseract_cmd = args.link
# r'C:\Users\z0042j7c\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img2char = pytesseract.image_to_string(img)
        flash("Extracted Text from the Image: "+ img2char)
        matches = list(datefinder.find_dates(img2char))
        print(matches)
        if len(matches) > 0:
            # date returned will be a datetime.datetime object. here we are only using the first match.
            date = matches[0]
            if date is None:
                flash("Date: ", date)
            else:
                flash("Date: Date Not Found")

        return render_template('upload.html', filename=filename)



    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):

    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == "__main__":
    app.run()
