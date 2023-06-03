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
        response = requests.post(url, files={'file': open(file_path, 'rb')})

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
    response = requests.get("http://localhost:5000/")

    print(response.text)


if __name__ == "__main__":
    main()