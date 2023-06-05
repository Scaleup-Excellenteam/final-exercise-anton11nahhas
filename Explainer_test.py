import unittest
import subprocess
import requests
import openai
from flask import Flask
import re


class SystemTest(unittest.TestCase):
    def setUp(self):
        self.web_api_process = subprocess.Popen(["python", "webAPI.py"])
        self.explainer_process = subprocess.Popen(["python", "pptxAPP.py"])

    def tearDown(self):
        self.web_api_process.terminate()
        self.explainer_process.terminate()

    def test_upload_and_check_status(self):
        upload_process = subprocess.Popen(["python", "PythonClient.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                          text=True)
        upload_process.stdin.write("u\n")
        upload_process.stdin.flush()
        upload_process.stdin.write(r"C:\Users\User\Desktop\New folder\test.pptx")
        upload_process.stdin.flush()
        output, _ = upload_process.communicate()

        uid_match = re.search(r"Uploaded file with UID:\s*([a-fA-F\d-]+),", output)
        uid = uid_match.group(1) if uid_match else None

        self.assertIsNotNone(uid, "UID not found in the output")

        status_process = subprocess.Popen(["python", "PythonClient.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                          text=True)
        status_process.stdin.write("s\n")
        status_process.stdin.flush()
        status_process.stdin.write(uid + "\n")
        status_process.stdin.flush()
        status_output, _ = status_process.communicate()

        self.assertTrue("200 OK" in status_output, "Status code not found in the output")


if __name__ == '__main__':
    unittest.main()
