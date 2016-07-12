import onedrive
import cognitive
import uuid


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
        print(details)


def cognitive_flow():
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

    print(cog_client.detect(image_url="https://public-ch3302.files.1drv.com/y3mDneSDzz8eV9V319LdQHrCCKvjJeKohMvqe6IXotRrn_1ZhVvQWjJHmefFQSnZmKHtKVcxHBu2EE7tSvNRc-lIL5r_QWFVEBlAdAxkFTIJ0ACPkhIXq2S7nWnZhiXAyf2OsxDnqObH2jI5hfrD4AcJFD3iw0QkB06qx6mE9VhsakpPGPmy9z7aOSslJq6X3JQTEEUMuHZeridUiO3qAW-4bE1wX56YI3H8M9Cc8OV53E78P-3yMxZ0xKp23H-yiPt"))

# cognitive_flow()
onedrive_flow()
