import uuid
import os
from datetime import datetime
from flask import Flask, request, jsonify

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

    # Generate UID
    uid = str(uuid.uuid4())

    # Save file with modified filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = secure_filename(file.filename)
    new_filename = f"{filename}_{timestamp}_{uid}"
    file.save(os.path.join(webAPI.config['UPLOAD_FOLDER'], new_filename))

    return jsonify({'uid': uid}), 200


@webAPI.route("/status/<int:uid>", methods=['GET'])
def upload_file(uid):
    pass


if __name__ == "__main__":
    webAPI.run(debug=True)