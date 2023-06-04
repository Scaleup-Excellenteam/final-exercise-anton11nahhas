import uuid
import os
from datetime import datetime
from flask import Flask, request, jsonify
import json

webAPI = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')
webAPI.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
webAPI.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER


@webAPI.route("/upload", methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file attached'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    uid = str(uuid.uuid4())
    original_filename, file_extension = os.path.splitext(file.filename)
    new_filename = f"{original_filename}_{timestamp}_{uid}{file_extension}"
    file.save(os.path.join(webAPI.config['UPLOAD_FOLDER'], new_filename))

    return jsonify({'uid': uid}), 200


@webAPI.route("/status/<string:uid>", methods=['GET'])
def get_status(uid):
    print(uid)
    output_folder = webAPI.config['OUTPUT_FOLDER']
    upload_folder = webAPI.config['UPLOAD_FOLDER']
    upload_files = [file for file in os.listdir(upload_folder) if uid in file]
    files = [file for file in os.listdir(output_folder) if uid in file]

    if not upload_files:
        filename = "no such file"
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        formatted_timestamp = datetime.now().isoformat()
        return jsonify({
            'status': 'not found',
            'filename': filename,
            'timestamp': formatted_timestamp,
            'explanation': 'None'
        }), 200

    if not files:
        filename = "no explanation file yet"
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        formatted_timestamp = datetime.now().isoformat()
        return jsonify({
            'status': 'pending',
            'filename': filename,
            'timestamp': formatted_timestamp,
            'explanation': 'None'
        }), 200

    file_path = os.path.join(output_folder, files[0])
    filename = os.path.basename(file_path)
    timestamp = filename.split('_')[1]
    formatted_timestamp = datetime.strptime(timestamp, '%Y%m%d%H%M%S').isoformat()

    with open(file_path) as f:
        explanation = json.load(f)
    status = 'done'

    return jsonify({
        'status': status,
        'filename': filename,
        'timestamp': formatted_timestamp,
        'explanation': explanation
    }), 200


if __name__ == "__main__":
    webAPI.run(debug=True)
