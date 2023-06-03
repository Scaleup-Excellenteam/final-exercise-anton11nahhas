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
        data = {'file_path': file_path}
        response = requests.post(url, json=data)

        if response.ok:
            return response.json()['UID']
        else:
            raise Exception(f"Upload failed. Status code: {response.status_code}")

    def status(self, uid):
        url = self.base_url + '/status'
        params = {'uid': uid}
        response = requests.get(url, params=params)

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
    client = PythonClient("http://localhost:5000/")
    powerpoint_UID = client.upload("C:\Users\User\Desktop\ביןתאוריה למעשה\בין-תאוריה-למעשה-תרגיל2.pptx")
    print(f"uploaded file with UID: {powerpoint_UID}")

    status = client.status(powerpoint_UID)
    if status.is_done():
        print("File upload is complete.")
    else:
        print("File upload is still in progress.")

    print(f"Status: {status.status}")
    print(f"Filename: {status.filename}")
    print(f"Timestamp: {status.timestamp}")
    print(f"Explanation: {status.explanation}")


if __name__ == "__main__":
    main()