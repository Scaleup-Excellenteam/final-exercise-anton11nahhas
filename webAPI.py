import uuid
import os
from datetime import datetime
from flask import Flask, request, jsonify
import json

webAPI = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')
webAPI.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
webAPI.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
webAPI.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
ERROR = 400
NOT_FOUND = 404
OK = 200
PENDING = 'pending'
DONE = 'done'
NONE = 'None'
TIME_FORMAT = '%Y%m%d%H%M%S'
NOT_FOUND_MESSAGE = 'not found'
NO_FILE_ATTACHED = 'No file attached'
EMPTY_FILENAME = 'Empty filename'
NO_EXPLANATION_FILE = 'No explanation file yet'


@webAPI.route("/upload", methods=['POST'])
def upload_file():
    """
    This end-point handles the '/upload' route that receives post requests to upload new files. The end-point firstly
    extracts the attached file from the request, verifies it, generates a universal unique ID, adds a time-stamp and
     the ID to the file-name, uploads the file to the 'uploads' folder and finally returns the UID as a response
     with a status code 'OK'
    :return: UID as a json responser (code: 200), or error with the error message as a json response (code 404)
    """
    if 'file' not in request.files:
        return jsonify({'error': NO_FILE_ATTACHED}), ERROR

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': EMPTY_FILENAME}), ERROR

    timestamp = datetime.now().strftime(TIME_FORMAT)
    uid = str(uuid.uuid4())
    original_filename, file_extension = os.path.splitext(file.filename)
    new_filename = f"{original_filename}_{timestamp}_{uid}{file_extension}"
    file.save(os.path.join(webAPI.config['UPLOAD_FOLDER'], new_filename))

    return jsonify({'uid': uid}), OK


@webAPI.route("/status/<string:uid>", methods=['GET'])
def get_status(uid):
    """
    This end-point handles the '/status' route that receives a get request with the uid as a part of the parameters.
    The end-point firstly configures all the needed files, check if the wanted uid found in any of the folders, and
    accordingly returns a suitable response.
    If the uid is not a valid one (not found in pending nor processed files) then return status code not found
    if the uid is not in the output file but is in the uploads file, then it is still pending and returns OK
    if the uid is found in the output file, then it mean it finished processing, extract the explanations and return
    it to the python client.
    :param uid: wanted unique ID (string)
    :return:
    """
    output_folder = webAPI.config['OUTPUT_FOLDER']
    processed_folder = webAPI.config['PROCESSED_FOLDER']
    upload_folder = webAPI.config['UPLOAD_FOLDER']

    upload_files = [file for file in os.listdir(upload_folder) if uid in file]
    processed_files = [file for file in os.listdir(processed_folder) if uid in file]
    output_files = [file for file in os.listdir(output_folder) if uid in file]

    if not processed_files and not upload_files:
        return jsonify({'status': NOT_FOUND_MESSAGE}), NOT_FOUND

    if not output_files:
        filename = NO_EXPLANATION_FILE
        timestamp = datetime.now().strftime(TIME_FORMAT)
        formatted_timestamp = datetime.now().isoformat()
        return generate_response(PENDING, filename, formatted_timestamp, NONE)

    file_path = os.path.join(output_folder, output_files[0])
    filename = os.path.basename(file_path)
    timestamp = filename.split('_')[1]
    formatted_timestamp = datetime.strptime(timestamp, TIME_FORMAT).isoformat()

    with open(file_path) as f:
        explanation = json.load(f)

    return generate_response(DONE, filename, formatted_timestamp, explanation)


def generate_response(status, filename, formatted_timestamp, explanation):
    """
    This method handles the return response for the get_status end-point, it receives a status, filename, timestamp
    and the explanations. Possible values of each of those:
    if the file is still processing:
    status is pending, filename: indicative message telling the user there is not output file name yet, timestamp:
    current time, explanations: None
    if the file finished processing:
    status: done, filename: the name of the explanations file, timestamp: current time, explanations: the explained
    content of the power-point.
    :param status: (string)
    :param filename: (string)
    :param formatted_timestamp: (string)
    :param explanation: (string)
    :return:
    """
    return jsonify({
        'status': status,
        'filename': filename,
        'timestamp': formatted_timestamp,
        'explanation': explanation
    }), OK


if __name__ == "__main__":
    webAPI.run(debug=True)
