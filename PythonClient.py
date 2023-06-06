import requests
from datetime import datetime
from dataclasses import dataclass


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


class PythonClient:
    """
    The class has a single member, the base_url, which is the url and the port the web API is listening to.
    The class has also two methods, upload and get status.
    """
    def __init__(self, base_url):
        self.base_url = base_url

    def upload(self, file_path):
        """
        The upload method receives a file_path which is the power-point presentation the user wants to be explained.
        the method handles a POST fetch to the /upload end-point. The method as well uses the 'requests' module to
        attach the power-point Presentation, Handles the response which is the UID created by the web API. and returns
        it to the user. The method handles exceptions as well, if the upload has failed.
        :param file_path: path of the power-point presentation (String)
        :return: UID created by web API (json)
        """
        url = self.base_url + '/upload'
        files = {'file': open(file_path, 'rb')}
        response = requests.post(url, files=files)

        if response.ok:
            return response.json()['uid']
        else:
            raise Exception(f"Upload failed. Status code: {response.status_code}")

    def status(self, uid):
        """
        The status method receives an uid, adds it as a parameter to the request, and fetches a get request to the
        /get_status end-point. The response received from the request is then handled and returned as json.
        :param uid: UID of the wanted file (String).
        :return: json response that has data about the status, filename, timestamp and explanations (JSON).
        """
        url = self.base_url + f'/status/{uid}'
        response = requests.get(url)

        if response.ok:
            json_data = response.json()
            return Status(
                status=json_data['status'],
                filename=json_data['filename'],
                timestamp=datetime.fromisoformat(json_data['timestamp']),
                explanation=json_data['explanation']
            )
        else:
            raise Exception(f"Status retrieval failed. Status code: {response.status_code}")


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
        if task.lower() == 'u':
            powerpoint_path = input("Enter a path for a powerpoint presentation: ")
            powerpoint_UID = client.upload(powerpoint_path)
            print(f"Uploaded file with UID: {powerpoint_UID}, please save the UID so you can get the status of the "
                  f"file when needed.")
        elif task.lower() == 's':
            powerpoint_UID = input("Please enter the UID of the file to get its status: ")
            status = client.status(str(powerpoint_UID))
            print(f"Status: {status.status}")
            print(f"Filename: {status.filename}")
            print(f"Timestamp: {status.timestamp}")

            if status.is_done():
                print("File upload is complete.")
                print(f"Explanation: {status.explanation}")
            else:
                print("File upload is still in progress.")
        elif task.lower() == 'q':
            break


if __name__ == "__main__":
    main()
