import requests
import json
import uuid
import base64
from urllib.parse import urlencode


class Contacts(object):
    """
    Reference: https://dev.outlook.com/restapi/tutorial/python
    """

    CLIENT_ID = "3bb59601-310c-4af1-bf6d-35340cd340c9"
    CLIENT_SECRET = "ZKBsnoZZkL8XxcqSdVodAEZ"
    REDIRECT_URL = "https://github.com/varunagrawal/OneGroup"

    email = "varunagrawal@outlook.com"

    # Constant strings for OAuth2 flow
    # The OAuth authority
    authority = 'https://login.microsoftonline.com'

    # The authorize URL that initiates the OAuth2 client credential flow for admin consent
    authorize_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/authorize?{0}')

    # The token issuing endpoint
    token_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/token')

    # The scopes required by the app
    scopes = ['openid',
              'https://outlook.office.com/mail.read',
              'https://outlook.office.com/contacts.read']

    outlook_api_endpoint = 'https://outlook.office.com/api/v2.0{0}'

    def __init__(self):
        super()
        self.token = None
        self.id_token = None
        self.token_expires_in = None

    def get_signin_url(self):
        """
        Generate the signin URL given the auth info
        This will return the auth code as a query param
        :return:
        """
        params = {'client_id': self.CLIENT_ID,
                  'redirect_uri': self.REDIRECT_URL,
                  'response_type': 'code',
                  'scope': ' '.join(str(i) for i in self.scopes)
                  }
        signin_url = self.authorize_url.format(urlencode(params))
        return signin_url

    def authenticate(self):
        """
        Gets the authentication token given the auth code
        :return:
        """
        auth_code = input("Please enter the auth code: ") or "M2086d442-02c2-6cb1-6ac7-330d5ebf67d0"
        # Build the post form for the token request
        post_data = {'grant_type': 'authorization_code',
                     'code': auth_code,
                     'redirect_uri': self.REDIRECT_URL,
                     'scope': ' '.join(str(i) for i in self.scopes),
                     'client_id': self.CLIENT_ID,
                     'client_secret': self.CLIENT_SECRET
                     }
        r = requests.post(self.token_url, data=post_data)
        try:
            auth = r.json()
            self.token = auth['access_token']
            print(self.token)
            self.id_token = auth['id_token']
            return auth
        except (Exception,):
            return 'Error retrieving token: {0} - {1}'.format(r.status_code, r.text)

    def get_all_contacts(self):
        # Use OData query parameters to control the results
        #  - Only first 10 results returned
        #  - Only return the GivenName, Surname, and EmailAddresses fields
        #  - Sort the results by the GivenName field in ascending order
        query_parameters = {'$select': 'GivenName,Surname,EmailAddresses',
                            '$top': '10',
                            '$orderby': 'GivenName ASC'}

        contacts_url = self.outlook_api_endpoint.format("/me/contacts")

        r = self.make_api_call('GET', contacts_url, self.token, self.email, parameters=query_parameters)

        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            return "{0}: {1}".format(r.status_code, r.text)

    def make_api_call(self, method, url, token, user_email, payload=None, parameters=None):
        # Send these headers with all API calls
        headers = {'User-Agent': 'python_tutorial/1.0',
                   'Authorization': 'Bearer {0}'.format(token),
                   'Accept': 'application/json',
                   'X-AnchorMailbox': user_email}

        print(headers)
        # Use these headers to instrument calls. Makes it easier
        # to correlate requests and responses in case of problems
        # and is a recommended best practice.
        request_id = str(uuid.uuid4())
        instrumentation = {'client-request-id': request_id,
                           'return-client-request-id': 'true'}

        headers.update(instrumentation)

        response = None

        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=parameters)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, params=parameters)
        elif method.upper() == 'PATCH':
            headers.update({'Content-Type': 'application/json'})
            response = requests.patch(url, headers=headers, data=json.dumps(payload), params=parameters)
        elif method.upper() == 'POST':
            headers.update({'Content-Type': 'application/json'})
            response = requests.post(url, headers=headers, data=json.dumps(payload), params=parameters)

        print(response.url)
        return response

    def get_user_email_from_id_token(self):
        # JWT is in three parts, header, token, and signature
        # separated by '.'
        token_parts = self.id_token.split('.')
        encoded_token = token_parts[1]

        # base64 strings should have a length divisible by 4
        # If this one doesn't, add the '=' padding to fix it
        leftovers = len(encoded_token) % 4
        if leftovers == 2:
            encoded_token += '=='
        elif leftovers == 3:
            encoded_token += '='

        # URL-safe base64 decode the token parts
        decoded = base64.urlsafe_b64decode(encoded_token.encode('utf-8')).decode('utf-8')

        # Load decoded token into a JSON object
        jwt = json.loads(decoded)

        return jwt
