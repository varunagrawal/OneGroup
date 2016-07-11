import requests
import uuid

class Face:

    KEY = "d53c4b9babfd43b0b0812e24d8f904df"

    def request_headers(self):
        headers = {"Ocp-Apim-Subscription-Key": self.KEY,
                   "Content-Type": "application/json"}
        return headers

    def add_person(self, person, person_group_id, person_data):
        url = "https://api.projectoxford.ai/face/v1.0/persongroups/{personGroupId}/persons".format(
            personGroupId=person_group_id)
        data = {"name": person,
                "userData": person_data}

        r = requests.post(url, header=self.request_headers(), data=data)
        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            return "{0}: {1}".format(r.status_code, r.text)

    def create_person_group(self, person_group_id):
        url = "https://api.projectoxford.ai/face/v1.0/persongroups/{personGroupId}".format(personGroupId=person_group_id)
        data = {"name": "varun_group",
                "userData": "Test group for MS Faculty Summit"}

        r = requests.put(url, headers=self.request_headers(), data=data)

        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            return "{0}: {1}".format(r.status_code, r.text)

    def identify(self, url, image_url):
        data = {"url": image_url}

        r = requests.post(url, headers=self.request_headers(), data=data)

        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            return "{0}: {1}".format(r.status_code, r.text)
