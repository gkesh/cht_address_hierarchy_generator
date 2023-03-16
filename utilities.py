from os import getenv

import csv
import json
import re
import secrets
import string


def parentize(child: str, parent: dict = None) -> dict:
    return {
        "_id": child,
        "parent": parent
    } if parent is not None else {
        "_id": child
    }

def load_locations(filename: str):
    with open(filename, "r") as f:
        return json.load(f)

def get_password() -> str:
    alphanumerals = string.ascii_letters + string.digits

    pwd = ''
    pwd_length = 8
    pwd_satisfied = False

    while not pwd_satisfied:
        pwd = ''.join([ secrets.choice(alphanumerals) for i in range(pwd_length) ])

        checkUpper = re.search(r"\d", pwd) is not None
        checkLower = re.search(r"[A-Z]", pwd) is not None
        checkDigit = re.search(r"[a-z]", pwd) is not None

        pwd_satisfied = checkDigit and checkLower and checkUpper

    return pwd

def search_contact(code: str) -> str:
    contacts_file = getenv("CONTACTS_FILE")
    with open(contacts_file, "r", encoding="utf-8") as con:
        con_reader = csv.reader(con, delimiter=",")
        for row in con_reader:
            if code == row[0].strip():
                print(row[1].strip())
                return row[1].strip()

        print(f"Code not found: {code}")
        return None

