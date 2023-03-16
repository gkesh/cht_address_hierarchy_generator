from json import loads
from os import getenv

import base64
import requests


def encode_credentials(username: str, password: str) -> str:
    credentials = bytes(f"{username}:{password}", "utf-8")
    return base64.b64encode(credentials).decode()


def create_header(credentials: str) -> dict:
    return {
        "Accept": "application/json",
        "Authorization": f"Basic {credentials}"
    }


def parse(request):
    def inner(*args, **kwargs):
        response = request(*args, **kwargs)

        success_codes = [200, 201]

        if response.status_code not in success_codes:
            print(response.json())
            return None
        
        return loads(response.text)
    return inner


def credentialize(request):
    def inner(*args):
        username = getenv("MEDIC_USERNAME")
        password = getenv("MEDIC_PASSWORD")    

        credentials = encode_credentials(username, password)
        return request(*args, credentials=credentials)
    return inner


@parse
@credentialize
def post(url: str, data: dict, **kwargs) -> dict:
    credentials = kwargs["credentials"]

    if not credentials:
        print("No credentials available")
        return None

    if data is None:
        print("Empty data provided to medic client")
        return None

    return requests.post(
        url,
        headers=create_header(credentials),
        json=data,
        verify=False
    )
