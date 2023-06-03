import uuid
import os
from datetime import datetime
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import glob
import json

webAPI = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
webAPI.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
webAPI.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER


@webAPI.route("/upload", methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file attached'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    uid = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    filename = os.path.basename(file.filename)
    new_filename = f"{filename}_{uid}{file_extension}"
    file.save(os.path.join(webAPI.config['UPLOAD_FOLDER'], new_filename))

    return jsonify({'uid': uid}), 200


@webAPI.route("/status/<string:uid>", methods=['GET'])
def get_status(uid):
    files = glob.glob(os.path.join(webAPI.config['OUTPUT_FOLDER'], f".*_{uid}_explanations.json"))

    if not files:
        filename = f"upload_{uid}_explanations.json"
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        formatted_timestamp = datetime.now().isoformat()
        return jsonify({
            'status': 'pending',
            'filename': filename,
            'timestamp': formatted_timestamp,
            'explanation': 'None'
        }), 200

    file_path = files[0]
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
