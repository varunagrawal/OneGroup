import requests
import uuid
import json


class Face:

    KEY = "d53c4b9babfd43b0b0812e24d8f904df"

    def request_headers(self):
        headers = {"Ocp-Apim-Subscription-Key": self.KEY,
                   "Content-Type": "application/json"}
        return headers

    def add_person(self, person_group_id, person_name, person_data):
        """
        https://dev.projectoxford.ai/docs/services/563879b61984550e40cbbe8d/operations/563879b61984550f3039523c
        :param person_group_id:
        :param person_name:
        :param person_data:
        :return:
        """
        url = "https://api.projectoxford.ai/face/v1.0/persongroups/{personGroupId}/persons"\
            .format(personGroupId=person_group_id)
        data = {"name": person_name,
                "userData": person_data}

        r = requests.post(url, headers=self.request_headers(), data=json.dumps(data))
        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            return "{0}: {1}".format(r.status_code, r.text)

    def add_person_face(self, person_image_url, person_group_id, target_face):
        """
        https://dev.projectoxford.ai/docs/services/563879b61984550e40cbbe8d/operations/563879b61984550f3039523b
        :param person_image_url:
        :param person_group_id:
        :param target_face:
        :return:
        """
        url = "https://api.projectoxford.ai/face/v1.0/persongroups/{personGroupId}/persons/{personId}/persistedFaces"\
            .format(personGroupId=person_group_id)
        data = {"url": person_image_url}
        params = {"targetFace": "{left},{top},{width},{height}".format(left=target_face["left"],
                                                                       top=target_face["top"],
                                                                       width=target_face["width"],
                                                                       height=target_face["height"])}

        r = requests.post(url, header=self.request_headers(), data=json.dumps(data), params=params)
        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            return "{0}: {1}".format(r.status_code, r.text)

    def create_person_group(self, person_group_id):
        url = "https://api.projectoxford.ai/face/v1.0/persongroups/{personGroupId}".format(
            personGroupId=person_group_id)
        data = {"name": "varun_group",
                "userData": "Test group for MS Faculty Summit"}

        r = requests.put(url, headers=self.request_headers(), data=json.dumps(data))

        if r.status_code == requests.codes.ok:
            return True
        else:
            resp = r.json()
            print(resp["error"]["message"])
            return False

    def delete_person_group(self, person_group_id):
        url = "https://api.projectoxford.ai/face/v1.0/persongroups/{personGroupId}".format(
            personGroupId=person_group_id)

        r = requests.delete(url, headers=self.request_headers())

        if r.status_code == requests.codes.ok:
            return True
        else:
            return False

    def train(self, person_group_id):
        url = "https://api.projectoxford.ai/face/v1.0/persongroups/{personGroupId}/train".format(
            personGroupId=person_group_id)

        r = requests.post(url, headers=self.request_headers())
        if r.status_code == 202:
            return r.json()
        else:
            return "{0}: {1}".format(r.status_code, r.text)

    def detect(self, image_url):
        url = "https://api.projectoxford.ai/face/v1.0/detect"
        data = {"url": image_url}

        r = requests.post(url, headers=self.request_headers(), data=json.dumps(data))

        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            return "{0}: {1}".format(r.status_code, r.text)

    def identify(self, image_url):
        url = "https://api.projectoxford.ai/face/v1.0/identify"
        data = {"url": image_url}

        r = requests.post(url, headers=self.request_headers(), data=json.dumps(data))

        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            return "{0}: {1}".format(r.status_code, r.text)
