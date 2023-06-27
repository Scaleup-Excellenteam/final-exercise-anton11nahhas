import requests
from datetime import datetime
from dataclasses import dataclass
import os
import re

NOT_FOUND = 404
ERROR = 400
OK = 200


@dataclass
class Status:
    """
    This class uses dataclass decorator, has 4 members,
    Status:
    1) Pending - the file did not finish processing yet.
    2) Done - the file has finished processing.
    3) Not found - the UID provided does not exist in the uploads/processed files.
    Filename:
    1) no explanation file yet, then there is no name (when the status = pending).
    2) the filename of the explanation file or the file that has been processed ( when status = done).
    Timestamp: simply the time when the status has been changed.
    Explanation:
    1) None: if the status is pending
    2) the explanations of the slides if the status is done.
    """
    status: str
    filename: str
    timestamp: datetime
    explanation: str

    def is_done(self):
        """
        This method updates the status to done to indicate the file is done processing.
        :return: Returns True if the status is done, false otherwise.
        """
        return self.status == 'done'


def handle_response(response):
    json_data = response.json()
    return Status(
        status=json_data['status'],
        filename=json_data['filename'],
        timestamp=datetime.fromisoformat(json_data['timestamp']),
        explanation=json_data['explanation']
    )


class PythonClient:
    """
    The class has a single member, the base_url, which is the url and the port the web API is listening to.
    The class has also two methods, upload and get status.
    """
    def __init__(self, base_url):
        self.base_url = base_url

    def upload(self, file_path, email):
        """
        The upload method receives a file_path which is the power-point presentation the user wants to be explained.
        the method handles a POST fetch to the /upload end-point. The method as well uses the 'requests' module to
        attach the power-point Presentation, Handles the response which is the UID created by the web API. and returns
        it to the user. The method handles exceptions as well, if the upload has failed.
        :param file_path: path of the power-point presentation (String)
        :return: UID created by web API (json)
        """

        if not email:
            email = ""
        url = self.base_url + f'/upload/{email}'
        files = {'file': open(file_path, 'rb')}
        response = requests.post(url, files=files)

        if response.ok:
            return response.json()['uid']
        else:
            raise Exception(f"Upload failed. Status code: {response.status_code}")

    def status(self, uid=None, email=None, filename=None):
        """
        The status method retrieves the status based on either UID or email and filename.
        If UID is provided, it fetches the status using the UID.
        If email and filename are provided, it fetches the status using email and filename as parameters.
        :param uid: UID of the file (optional)
        :param email: Email of the file (optional)
        :param filename: Filename of the file (optional)
        :return: Status object containing the status, filename, timestamp, and explanation
        """

        if uid:
            url = self.base_url + f'/status/{uid}'
            response = requests.get(url)
        elif email and filename:
            url = self.base_url + '/status'
            params = {
                'email': email,
                'filename': filename
            }
            response = requests.get(url, params=params)
        else:
            raise ValueError("Please provide either UID or email and filename.")

        if response.ok:
            return handle_response(response)
        elif response.status_code == NOT_FOUND:
            print("UID not found")
            return handle_response(response)
        else:
            raise Exception(f"Status retrieval failed. Status code: {response.status_code}")


def is_email_format(string):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    match = re.match(pattern, string)
    return match is not None


def print_status_results(status):
    print(f"Status: {status.status}")
    print(f"Filename: {status.filename}")
    print(f"Timestamp: {status.timestamp}")

    if status.is_done():
        print("File upload is complete.")
        print(f"Explanation: {status.explanation}")
    else:
        print("File upload is still in progress.")


def main():
    """
    Implemented a main function that runs in an infinite loop that asks the user for which operation he wants to
    perform, depending on the operation, the user is required to provide an input. The method creates an object of
    PythonClient which initiates the connection with the server.
    :return:
    """
    client = PythonClient("http://localhost:5000")

    while True:
        task = input("which task do you want to use? 'u' for uploading new files, 's' to get the status of a file,"
                     "or 'q' to exit: ")
        if not task.lower() == 'u' and not task.lower() == 's' and not task.lower() == 'q':
            print("please enter a valid option.")
            continue
        elif task.lower() == 'u':
            user_email = input("Please provide your email(optional, press enter for anonymous upload): ")
            if user_email:
                if not is_email_format(user_email):
                    print("Please provide a valid email.")
                    continue

            powerpoint_path = input("Enter a path for a powerpoint presentation: ")
            if not os.path.exists(powerpoint_path):
                print("the path provided is not valid please provide a file on you computer.")
                continue

            powerpoint_UID = client.upload(powerpoint_path, user_email)
            print(f"Uploaded file with UID: {powerpoint_UID}, please save the UID so you can get the status of the "
                  f"file when needed.")
        elif task.lower() == 's':
            status_task = input("do you want to retrieve status by uid ('1') or by providing an email and a file_name('2')")
            if status_task == '1':
                powerpoint_UID = input("Please enter the UID of the file to get its status: ")
                status = client.status(uid=str(powerpoint_UID))
                print_status_results(status)
            elif status_task == '2':
                email = input("Please enter an email: ")
                if not is_email_format(email):
                    print("Please provide a valid email.")
                    continue
                file_name = input("Please enter the desired file_name: ")
                status = client.status(email=email, filename=file_name)
                print_status_results(status)
            else:
                print("please enter a valid option, '1' for uid, '2' for a file_name and email.")
                continue

        elif task.lower() == 'q':
            break


if __name__ == "__main__":
    main()
