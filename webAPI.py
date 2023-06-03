import uuid
import os
from datetime import datetime
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import glob
import json

webAPI = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
webAPI.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@webAPI.route("/upload", methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file attached'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    uid = str(uuid.uuid4())

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = secure_filename(file.filename)
    new_filename = f"{filename}_{timestamp}_{uid}"
    file.save(os.path.join(webAPI.config['UPLOAD_FOLDER'], new_filename))

    return jsonify({'uid': uid}), 200


@webAPI.route("/status/<int:uid>", methods=['GET'])
def get_status(uid):
    files = glob.glob(os.path.join(webAPI.config['UPLOAD_FOLDER'], f"*_{uid}"))
    if not files:
        return jsonify({'status': 'not found'}), 404

    file_path = files[0]
    filename = os.path.basename(file_path)
    timestamp = filename.split('_')[1]

    output_filename = f"{filename}_output.json"
    output_file_path = os.path.join(webAPI.config['UPLOAD_FOLDER'], output_filename)
    if os.path.exists(output_file_path):
        with open(output_file_path) as f:
            explanation = json.load(f)
        status = 'done'
    else:
        explanation = None
        status = 'pending'

    return jsonify({
        'status': status,
        'filename': filename,
        'timestamp': timestamp,
        'explanation': explanation
    }), 200


if __name__ == "__main__":
    webAPI.run(debug=True)
