import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onegroup.settings")

import django
django.setup()

from outlook.models import Contact
import onedrive_module as onedrive
import cognitive_module as cognitive
import argparse
from datetime import datetime
from PIL import Image, ImageDraw
from io import BytesIO
import requests
import sys


cog_client = cognitive.Face()
group_id = "varun"


def onedrive_flow():
    od_client = onedrive.OneDrive("varunagrawal@outlook.com")
    result = od_client.get_folder_children(folder="approot")

    for idx, item in enumerate(result["value"]):
        # item keys are
        # ['parentReference', 'size', '@content.downloadUrl', 'eTag', 'webUrl', 'photo', 'file', 'image',
        # 'createdBy', 'lastModifiedBy', 'lastModifiedDateTime',
        # 'fileSystemInfo', 'cTag', 'createdDateTime', 'name', 'id']
        details = "{3}: {0}={1}\n\tLocation: {2}\n\tDownload: {4}\nTime taken: {5}".format(item["id"], item["name"],
                                                      item["webUrl"], idx, item["@content.downloadUrl"], item["photo"]["takenDateTime"])
        print(details)
        print("\n\n")

    # od_client.add_webhook_subscription()


def train_person():
    parser = argparse.ArgumentParser(description='Train Person Face')
    parser.add_argument('person_name', type=str, help='The name of the person being trained')
    parser.add_argument('image_url', type=str, help="The image URL with the person face")
    parser.add_argument('--person_id', required=False, type=str, help="The person ID as given by the Cognitive API")

    args = parser.parse_args()


def detect(image_url):
    results = cog_client.detect(image_url=image_url)

    print("Detection results:")
    print(results)

    file = requests.get(image_url)
    img = Image.open(BytesIO(file.content))

    # img = img.rotate(90)

    print(img.size)

    draw = ImageDraw.Draw(img)

    for face in results:
        rect = face['faceRectangle']
        x1, y1 = rect["left"], rect["top"]
        x2, y2 = x1 + rect["width"], y1 + rect["height"]

        draw.rectangle([(x1, y1), (x2, y2)])

    img.show()

    return results


def register(name, email, image_url, last_modified, face_rect=[]):
    """

    :param name:
    :type name:
    :param email: This is the email of the person in Outlook Contacts
    :type email:
    :param image_url:
    :type image_url:
    :param last_modified:
    :type last_modified:
    :param group_id:
    :type group_id:
    :param face_rect:
    :type face_rect:
    :return:
    :rtype:
    """

    person = Contact()
    person.name = name
    person.email = email

    resp = cog_client.add_person(person_group_id=group_id, person_name=name, person_data=email)
    print(resp)

    person.person_id = resp["personId"]
    person.group = group_id
    person.weight = 1
    person.last_tagged = datetime(last_modified)

    if len(cog_client.get_everyone_in_group(group_id)) > 1000:
        min_weight = 101
        id2delete = None
        id_time = None

        for contact in Contact.objects.all():
            if contact.weight < min_weight:
                min_weight = contact.weight
                id2delete = contact.face_id
                id_time = contact.last_tagged

            elif contact.weight == min_weight:
                if contact.last_tagged < id_time:
                    id2delete = contact.face_id
                    id_time = contact.last_tagged

        cog_client.delete_person(person_group_id=group_id, person_id=id2delete)

        cog_client.add_person(person_group_id=group_id, person_name=name, person_data=email)

    face_id = cog_client.add_person_face(image_url, person_group_id=person.group,
                                         person_id=person.person_id,
                                         target_face=face_rect)
    print(face_id)
    person.face_id = face_id["persistedFaceId"]
    person.save()

    cog_client.train(group_id)

    while cog_client.training_status(group_id)["status"] != "succeeded":
        pass

    print("Training completed!")


def identify(image_url):
    detections = detect(image_url)

    if len(detections) == 0:
        print("No faces in image")
        return False

    face_ids = []
    for detection in detections:
        face_ids.append(detection["faceId"])

    resp = cog_client.identify(image_url=image_url, person_group_id=group_id, face_ids=face_ids)
    print(resp)
    print("\n\n\n")

    for face in resp:
        if len(face["candidates"]) > 0:
            for candidate in face['candidates']:
                person_id = candidate["personId"]
                confidence = candidate['confidence']

                ######
                # We can use the confidence and last_tagged together here to identify the person more robustly

                who = cog_client.get_person(person_group_id=group_id, person_id=person_id)

                contact = Contact.objects.get()

                print("{0} identified in image [confidence={1}]".format(who["name"], confidence))
                print(who)
        else:
            print("This face cannot be identified. Informing NSA now!")


def cognitive_flow(train=True):
    # resp = cog_client.create_person_group(person_group_id=group_id)

    person_ids = {} or \
                 {'Varun': 'f2ef9c8b-2ffe-478e-8e7f-e775bda3429e', 'Preeti': '7eba292d-f902-4be3-a1c0-4ffca8ae9e90'}

    # persons = [("Varun", "Yours Truly"), ("Preeti", "Preeti Ramaraj")]
    persons = [("Preeti", "Preeti Ramaraj")]

    if True:
        for name, data in persons:
            resp = cog_client.add_person(person_group_id=group_id, person_name=name, person_data=data)
            person_ids[name] = resp["personId"]

    print(person_ids)

    if train:
        # View the image https://1drv.ms/i/s!AO18pri6pxSNktNI
        image_url = "https://public-ch3302.files.1drv.com/y3mb9lkGjSOmczdX575NBMU0jqQxpiboxfw-KJY8rWDW0nRKNbD2aogUrYMP0q1-Ll-e1EJKu-HsKQMMgN72NkrQJaqYGxnZFKz0xuwVgY4NZDqWEwithRo497sFGFJlr_tQNZf6WCM2BsIBL1mwKN8qPtc-UXle0g_KUbEplXcU_coJnH0rS6KRXyxSm_WxMWZdDJQAq0qS-mzYbU7wkkzi_PQgmvvusARmqnvBNL41a3KgkmFieeb8Ek8KPG4lADp"

        print(cog_client.detect(image_url=image_url))

        varun_face = {'faceRectangle': {'width': 494, 'top': 652, 'left': 31, 'height': 494},
                      'faceId': 'e99f463b-ec4c-4f25-b1c8-e84d4a85c76a'}
        preeti_face = {'faceRectangle': {'width': 352, 'top': 982, 'left': 616, 'height': 352},
                       'faceId': '5de78d95-6717-4d4b-86a0-0687ba5ac8e3'}

        varun_face_id = cog_client.add_person_face(image_url, person_group_id=group_id,
                                                   person_id=person_ids["Preeti"], target_face=preeti_face['faceRectangle'])
        print(varun_face_id)

        cog_client.train(group_id)

        while cog_client.training_status(group_id)["status"] != "succeeded":
            pass

        print("Training completed!")

    else:
        image_url = "https://public-ch3302.files.1drv.com/y3m863vZNV4hKrlU1_hm2-FO8uV9Pxhgsc62ijCouY7ISGLzy0yOkUBUBiRq8PQjEwpQ2cEBXQqp-yUVCaAefv5aq70-7e_i8-nzRELd_Xn-cMHaF3xp6uAgDB2_SonAemnkebBhl73xyhA_DUwFiwKu3FmK9ZdwQ2p41MyBnEikZ7Mch6a1Gp9q5LimYvIzhnwW2VbbQT5pyAQkIaPqy7KECuu1rQM_XSY8d6Vd7bdrCk-_fvjCDCNOd1LGyugYYPc"
        detections = cog_client.detect(image_url)

        if len(detections) == 0:
            print("No faces in image")
            return False

        face_ids = []
        for detection in detections:
            face_ids.append(detection["faceId"])

        resp = cog_client.identify(image_url=image_url, person_group_id=group_id, face_ids=face_ids)
        print(resp)
        for person in resp:
            if len(person["candidates"]) > 0:
                person_id = person["candidates"][0]["personId"]
                who = cog_client.get_person(person_group_id=group_id, person_id=person_id)
                print("{0} identified in image".format(who["name"]))
            else:
                print("This person is not in our system. Informing NSA now!")


def check_training_status():
    print(cog_client.training_status(group_id))

# Onedrive keeps regenerating the download links necessitating the need to run the onedrive flow again and again -_-
# onedrive_flow()

# cognitive_flow(train=True)

detect_url = "https://public-ch3302.files.1drv.com/y3mTKpYFXpAOrFaP_OVXlSoPsN6xBoBTPHMNSDWxksWheQGw7i_TkA-jpgb6QCCxvcDHNY64oMedWJvuMqZY9aG9C1ngXIbcCAyPw0M1hpoWVK-hYfOJW36WjaGDebIaittAaOvWM1-av49WlQVc-cXdIlDI52N1Tx1QXTq3Fc1nxuLKnEtonQFrPTT4wBzdv6x4mbQWzjtvulnYIkQfcgjXNgUge190UlJZRas0HqQwc2IAx3RnuqNIfUtWR-8dLIb"
detections = detect(detect_url)
print(detections)
register("Varun Agrawal", "varunagrawal@outlook.com",
         detect_url, last_modified="2015-02-22T07:23:04Z",
         face_rect=detections[0]['faceRectangle'])

# Test image
# url = "https://public-ch3302.files.1drv.com/y3m21ptnt4kJz5Btyy2Ybdt2DvNB-MTeUS0lZt9NoeM1HTSdupbFnxYsVCMKdbn_Nuk5EgJQ8UGd3hEngG-AK6m8d1lotbl1m1RVSUJSyuKBQafSEL8HgFUohsWLzGkaKdYFgxqmBGxWKPZH0RRiaC1Vt5tF_3faBSV1SNIgAxR7FHfQmR26ULHO9f7p8BjMDIarXHCFzrUjp7TOSFb_X5Pbzbq8JUbTpcJ-2yUw809qWD1JRIF6DE_cnyqnWjFYCiZ"
# detection_results = detect(image_url=url)

id_url = "https://public-ch3302.files.1drv.com/y3mxV0W1IM8eleStWacC6_DDlN6cGBurfRUk5YqJX9a0mUIQUre-h58FrkYrf7JG_Yk5J5-q9H05vb6wOpKcSOy3f3VvK0sTrbA5c4biSis3HZEKXQIR3SW5hM-oUDqEj9m02ZiqkzMT1rSu-_nZrbEPe9qkKj4lB_if7y_3R0D5vpoKGyX-DlzVRNjMwY4A73-yNL0B2KhaxfGhEKm5LKRTLmVXtMLti6bR8idu4lGerTwopxTjtF228amBSeacUWUyC3l-T2OoWfItOFoGf_K2g"

# person_id = "beb385eb-d9f4-442e-8cf9-1ae548e3beeb"
# cog_client.delete_person(person_group_id=group_id, person_id=person_id)

print(cog_client.get_everyone_in_group(group_id))

id_url2 = "https://public-ch3302.files.1drv.com/y3m-JucAqeUwGAL_e6cQMcVn77OAMhEzBAZnllt_P5hurNdEntk--CyvB_B0dIQgt9O9008G0Nqny164ghW8xc5fsNtsGC9znodNh7Z--oLWUK4GCkwqR0dvXH3ekhmw045W6VmJ5bi7Q3qlY1nDSBvAlG3p-62LJjJdFNqU0tz06pQt06kIKPI_a4FjctJNNZooYGH50B08DvSqeCpqCKQaiKkxgBf8ZAWdorlhYnFMLP8UIhztkuYyXgtYgHZPyh1"

# identify(id_url2)
