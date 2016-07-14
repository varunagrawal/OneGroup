import onedrive
import cognitive
import argparse


def onedrive_flow():
    od_client = onedrive.OneDrive("varunagrawal@outlook.com")
    result = od_client.get_folder_children(folder="approot")

    for idx, item in enumerate(result["value"]):
        # item keys are
        # ['parentReference', 'size', '@content.downloadUrl', 'eTag', 'webUrl', 'photo', 'file', 'image',
        # 'createdBy', 'lastModifiedBy', 'lastModifiedDateTime',
        # 'fileSystemInfo', 'cTag', 'createdDateTime', 'name', 'id']
        details = "{3}: {0}={1} @ {2} and {4}".format(item["id"], item["name"],
                                                      item["webUrl"], idx, item["@content.downloadUrl"])
        # print(details)

    od_client.add_webhook_subscription()


def train_person():
    parser = argparse.ArgumentParser(description='Train Person Face')
    parser.add_argument('person_name', type=str, help='The name of the person being trained')
    parser.add_argument('image_url', type=str, help="The image URL with the person face")
    parser.add_argument('--person_id', required=False, type=str, help="The person ID as given by the Cognitive API")

    args = parser.parse_args()


def cognitive_flow(train=True):
    cog_client = cognitive.Face()

    group_id = "varun"
    resp = cog_client.create_person_group(person_group_id=group_id)

    person_ids = {} or \
                 {'Varun': 'f2ef9c8b-2ffe-478e-8e7f-e775bda3429e', 'Preeti': '7eba292d-f902-4be3-a1c0-4ffca8ae9e90'}

    persons = [("Varun", "Yours Truly"), ("Preeti", "Preeti Ramaraj")]

    if not person_ids:
        for name, data in persons:
            resp = cog_client.add_person(person_group_id=group_id, person_name=name, person_data=data)
            person_ids[name] = resp["personId"]

    print(person_ids)

    if train:
        # View the image https://1drv.ms/i/s!AO18pri6pxSNktNI
        image_url = "https://public-ch3302.files.1drv.com/y3mQH9SQMNHsr3hUcMcw9PG3Z_5S8qc1eUpMu693s0qM45t-4Nt3vQiSmJzaAyPxPOjrKxrz-3y7gg9hxUYwNiWtTKm-YYMDdDcT5QseoJBb419qs2u0-aPFCm8C5AX5LaN6tJJZ5h69z2YPLtrxn9a7eA7rpJRwxi2n2peIH1hyaiSsscLvQZGd9v8bHX9b42_yyIaUTlwQeYG72bscGhKtGMlzKXQsJOTfi9uuqDshmWncrpIqni3uTh-QQ3cTNHV"

        print(cog_client.detect(image_url=image_url))

        varun_face = {'faceRectangle': {'width': 494, 'top': 652, 'left': 31, 'height': 494},
                      'faceId': 'e99f463b-ec4c-4f25-b1c8-e84d4a85c76a'}
        preeti_face = {'faceRectangle': {'width': 352, 'top': 982, 'left': 616, 'height': 352},
                       'faceId': '5de78d95-6717-4d4b-86a0-0687ba5ac8e3'}

        varun_face_id = cog_client.add_person_face(image_url, person_group_id=group_id,
                                                   person_id=person_ids["Varun"], target_face=varun_face['faceRectangle'])
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
    cog_client = cognitive.Face()
    group_id = "varun"
    print(cog_client.training_status(group_id))

# Onedrive keeps regenerating the download links necessitating the need to run the onedrive flow again and again -_-
onedrive_flow()

# cognitive_flow(train=False)
