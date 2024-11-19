from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
# from pycnc import PyCNC  # Import PyCNC
from datetime import datetime

app = Flask(__name__)

# Define the upload directory directly
UPLOAD_DIR = 'uploads/'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'gcode', 'nc', 'txt'}

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def allowed_file(filename):
    """
    Check if the file has an allowed extension.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Endpoint to upload a G-code file and execute it.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        # Secure the original filename
        original_filename = secure_filename(file.filename)
        # Get the file extension
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        # Generate a timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Create a new filename with timestamp
        new_filename = f"{original_filename.rsplit('.', 1)[0]}_{timestamp}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, new_filename)
        # Save the file
        file.save(file_path)

        try:
            # Initialize PyCNC
            # cnc = PyCNC()
            
            # # Run PyCNC with the uploaded G-code file
            # cnc.run(file_path)
            
            # # Optionally, delete the file after execution to save space
            # os.remove(file_path)
            print(f"THING ADDED {file_path}")
            
            return jsonify({'message': 'G-code executed successfully'}), 200
        except Exception as e:
            print("error")
            # Optionally, delete the file in case of an error
            # if os.path.exists(file_path):
            #     os.remove(file_path)
            # return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/')
def index():
    return '''
    <!doctype html>
    <title>Upload G-code File</title>
    <h1>Upload G-code File</h1>
    <form method=post enctype=multipart/form-data action="/upload">
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    # It's recommended to run Flask with a production server like Gunicorn in production
    app.run(host='0.0.0.0', port=5000)
