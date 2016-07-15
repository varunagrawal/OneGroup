from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
import requests
from urllib.parse import urlencode


CLIENT_ID = "3bb59601-310c-4af1-bf6d-35340cd340c9"
CLIENT_SECRET = "ZKBsnoZZkL8XxcqSdVodAEZ"
REDIRECT_URI = "http://localhost:8000/onedrive/authenticate"

API_URL = "https://api.onedrive.com/v1.0"
AUTH_SERVER_URL = "https://login.live.com/oauth20_authorize.srf"
AUTH_TOKEN_URL = "https://login.live.com/oauth20_token.srf"

scopes = ['wl.signin',
          'onedrive.readonly',
          'onedrive.appfolder']


def index(request):
    return HttpResponse("Welcome")


def login(request):
    params = {
        "client_id": CLIENT_ID,
        "scope": " ".join(scopes),
        "response_type": "code",
        "redirect_uri": REDIRECT_URI
    }
    auth_url = "{}?{}".format(AUTH_SERVER_URL, urlencode(params))

    return redirect(auth_url)


def webhook(request):
    validation_token = request.GET.get("validationToken", "Webhook called")
    return HttpResponse(validation_token)


def authenticate(request):
    code = request.GET["code"]
    params = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "resource": None,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(AUTH_TOKEN_URL, headers=headers, data=params).json()
    print(response)
    print(request.session)
    request.session["access_token"] = response["access_token"]

    return HttpResponseRedirect("/onedrive/approot/")


def approot(request):
    headers = {
        'User-Agent': 'onegroup/1.0',
        'Authorization': 'Bearer {0}'.format(request.session["access_token"]),
        'Accept': 'application/json',
        'X-AnchorMailbox': "varunagrawal@outlook.com"
    }

    url = API_URL + "/drive/special/approot/children"

    result = requests.get(url, headers=headers).json()
    images = []
    for idx, item in enumerate(result["value"]):
        # item keys are
        # ['parentReference', 'size', '@content.downloadUrl', 'eTag', 'webUrl', 'photo', 'file', 'image',
        # 'createdBy', 'lastModifiedBy', 'lastModifiedDateTime',
        # 'fileSystemInfo', 'cTag', 'createdDateTime', 'name', 'id']
        img = "<a href={0} alt={1}>{2}</a>".format(item["webUrl"], item["name"], item["@content.downloadUrl"])
        images.append(img)
        # "{3}: {0}={1} @ {2} and {4}".format(item["id"], item["name"], item["webUrl"], idx, item["@content.downloadUrl"])

    return render(request, 'approot.html', context={'images': images})
