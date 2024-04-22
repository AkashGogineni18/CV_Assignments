from flask import Flask, render_template, request
import cv2 as cv
import math
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Hardcoded camera matrix path
CAMERA_MATRIX_PATH = 'images/right/camera_matrix.txt'

def convert_milli_to_cm(x):
    x = x / 10
    return x / 25.4

def get_circle_diameter(image_path):
    # Load camera matrix
    camera_matrix = []
    with open(CAMERA_MATRIX_PATH, 'r') as f:
        for line in f:
            camera_matrix.append([float(num) for num in line.split()])

    # Load image
    image = cv.imread(image_path)

    # Define points (you may need to adjust these values)
    x, y, w, h = 15, 16, 13, 1
    Image_point1x = x
    Image_point1y = y
    Image_point2x = x + w
    Image_point2y = y + h

    # Draw rectangle and line on the image
    cv.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 5)
    cv.line(image, (Image_point1x, Image_point1y), (Image_point1x, Image_point2y), (0, 0, 255), 8)

    # Calculate real world points
    Z = 320
    FX = camera_matrix[0][0]
    FY = camera_matrix[1][1]
    Real_point1x = Z * (Image_point1x / FX)
    Real_point1y = Z * (Image_point1y / FY)
    Real_point2x = Z * (Image_point2x / FX)
    Real_point2y = Z * (Image_point2y / FY)

    # Calculate diameter in pixels
    dist = math.sqrt((Real_point2y - Real_point1y) ** 2 + (Real_point2x - Real_point1x) ** 2)

    # Draw dimensions result on the image
    font = cv.FONT_HERSHEY_SIMPLEX
    text = f'Diameter: {dist:.2f} cm'
    cv.putText(image, text, (10, 30), font, 1, (0, 0, 255), 2, cv.LINE_AA)

    # Save the image with drawn dimensions
    result_image_path = os.path.join(UPLOAD_FOLDER, 'result_image.jpg')
    cv.imwrite(result_image_path, image)

    return dist


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            diameter_cm = get_circle_diameter(file_path)
            return render_template('result.html', diameter=diameter_cm)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)