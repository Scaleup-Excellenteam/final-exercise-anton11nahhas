import requests
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Status:
    status: str
    filename: str
    timestamp: datetime
    explanation: str

    def is_done(self):
        return self.status == 'done'


class PythonClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def upload(self, file_path):
        url = self.base_url + '/upload'
        files = {'file': open(file_path, 'rb')}
        response = requests.post(url, files=files)

        if response.ok:
            return response.json()['uid']
        else:
            raise Exception(f"Upload failed. Status code: {response.status_code}")

    def status(self, uid):
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
    client = PythonClient("http://localhost:5000")
    powerpoint_UID = client.upload(r"C:\Users\User\Desktop\ביןתאוריה למעשה\בין-תאוריה-למעשה-תרגיל2.pptx")
    print(f"Uploaded file with UID: {powerpoint_UID}")

    while True:
        status = client.status(str(powerpoint_UID))
        print(f"Status: {status.status}")
        print(f"Filename: {status.filename}")
        print(f"Timestamp: {status.timestamp}")

        if status.is_done():
            print("File upload is complete.")
            print(f"Explanation: {status.explanation}")
            break
        else:
            print("File upload is still in progress.")

        choice = input("Press 'q' to quit or any other key to check status again: ")
        if choice.lower() == 'q':
            break


if __name__ == "__main__":
    main()
