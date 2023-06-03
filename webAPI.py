from flask import Flask, render_template, request, redirect

webAPI = Flask(__name__)

@webAPI.route("/upload/<string:file_path>", methods=['POST'])
def upload_file(file_path):
    pass


@webAPI.route("/status/<int:uid>", methods=['GET'])
def upload_file(uid):
    pass


if __name__ == "__main__":
    webAPI.run(debug=True)