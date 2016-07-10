import requests
from urllib.parse import urlencode

class Contacts(object):
    CLIENT_ID = "3bb59601-310c-4af1-bf6d-35340cd340c9"
    CLIENT_SECRET = "ZKBsnoZZkL8XxcqSdVodAEZ"
    REDIRECT_URL = "https://github.com/varunagrawal/OneGroup"

    # Constant strings for OAuth2 flow
    # The OAuth authority
    authority = 'https://login.microsoftonline.com'

    # The authorize URL that initiates the OAuth2 client credential flow for admin consent
    authorize_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/authorize?{0}')

    # The token issuing endpoint
    token_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/token')

    # The scopes required by the app
    scopes = ['openid',
              'https://outlook.office.com/contacts.read']

    def __init__(self):
        super()

    def get_signin_url(self):
        params = {'client_id': self.CLIENT_ID,
                  'redirect_uri': self.REDIRECT_URL,
                  'response_type': 'code',
                  'scope': ' '.join(str(i) for i in self.scopes)
                  }
        signin_url = self.authorize_url.format(urlencode(params))
        return signin_url

    def authenticate(self):
        pass

    def get_all(self):
        params = {'scope': "https://outlook.office.com/contacts.read"}
        r = requests.get("https://outlook.office.com/api/v2.0/me/contacts", params=params)
