import requests
from urllib.parse import urlencode
import json


class OneDrive:
    """
    References:
        https://graph.microsoft.io/en-us/docs/authorization/app_authorization
        https://dev.onedrive.com/readme.htm

    """

    CLIENT_ID = "3bb59601-310c-4af1-bf6d-35340cd340c9"
    CLIENT_SECRET = "ZKBsnoZZkL8XxcqSdVodAEZ"
    REDIRECT_URI = "https://github.com/varunagrawal/OneGroup"

    API_URL = "https://api.onedrive.com/v1.0"
    AUTH_SERVER_URL = "https://login.live.com/oauth20_authorize.srf"
    AUTH_TOKEN_URL = "https://login.live.com/oauth20_token.srf"

    scopes = ['wl.signin',
              'onedrive.readonly',
              'onedrive.appfolder']

    auth = {}

    def __init__(self, user_email):
        self.user_email = user_email

        self.get_auth_url()
        code = input("Please input the auth code: ")
        self.authenticate(code)

    def get_auth_url(self):
        params = {
            "client_id": self.CLIENT_ID,
            "scope": " ".join(self.scopes),
            "response_type": "code",
            "redirect_uri": self.REDIRECT_URI
        }
        auth_url = "{}?{}".format(self.AUTH_SERVER_URL, urlencode(params))

        # print out the auth url so that the user can get the auth code
        print("The auth url is:")
        print(auth_url)

    def authenticate(self, code):
        params = {
            "code": code,
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "redirect_uri": self.REDIRECT_URI,
            "grant_type": "authorization_code",
            "resource": None,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(self.AUTH_TOKEN_URL, headers=headers, data=params)

        self.auth = response.json()

    def headers(self):
        return {'User-Agent': 'onegroup/1.0',
                'Authorization': 'Bearer {0}'.format(self.auth["access_token"]),
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-AnchorMailbox': self.user_email}

    def get_folder_children(self, folder="cameraroll"):
        url = self.API_URL + "/drive/special/approot/children".format(folder)

        r = requests.get(url, headers=self.headers())
        return r.json()

    def add_webhook_subscription(self):
        url = self.API_URL + "/drive/special/approot/subscriptions"
        data = {
            "notificationUrl": "http://onegroup.herokuapp.com/onedrive/webhook",
            "expirationDateTime": "2017-01-01T11:23:00.000Z"
        }

        r = requests.post(url, headers=self.headers(), data=json.dumps(data))

        print(r.text)
