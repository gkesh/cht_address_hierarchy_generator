from client import post
from typing import Optional
from utilities import parentize, load_locations, get_password, search_contact
from os import getenv

import csv
import time


double_digit = lambda x: f"0{x}" if x < 10 else f"{x}"
couch_url = getenv("MEDIC_URL")
cht_url = getenv("CHT_URL")

def transform_locations(location: dict) -> dict:
    contact = {
        "type": "contact",
        "contact_type": location["type"],
        "name": location["name"],
        "external_id": "",
        "notes": "",
        "contact": "",
        "geolocation": "",
        "meta": {
            "created_by": "medic",
            "created_by_person_uuid": "",
            "created_by_place_uuid": ""
        },
        "reported_date": round(time.time() * 1000)
    }

    if "hhID" in location:
        contact["hhID"] = location["hhID"]

    if "place_code" in location:
        contact["place_code"] = location["place_code"]

    if "parent_code" in location:
        contact["parent_code"] = location["parent_code"]

    if "child" in location and location["child"] is not None:
        child = location["child"]
        if type(child) == list:
            if "child_type" in location:
                if location["child_type"] == "c40_municipality":
                    contact["child"] = [
                        transform_locations(
                            {
                                "name": item["name"],
                                "type": location["child_type"],
                                "place_code": item["code"],
                                "child": [
                                    {
                                        "name": f"Ward {num.split(':')[0]}", 
                                        "type": "c50_ward", 
                                        "place_code": f"{item['code']}-{num.split(':')[0]}-{num.split(':')[1]}",
                                        "child": [
                                            {
                                                "name": f"{item['code']}-{num.split(':')[0]}-{num.split(':')[1]}-{double_digit(i)} - Empty",
                                                "type": "c80_household",
                                                "place_code": f"{item['code']}-{num.split(':')[0]}-{num.split(':')[1]}-{double_digit(i)}",
                                                "hhID": f"{item['code']}-{num.split(':')[0]}-{num.split(':')[1]}-{double_digit(i)}",
                                                "child": [
                                                    {
                                                        "name": f"Empty",
                                                        "type": "c80_household_contact",
                                                        "parent_code": f"{item['code']}-{num.split(':')[0]}-{num.split(':')[1]}-{double_digit(i)}"
                                                    }
                                                ]
                                            } for i in range(1, 25)
                                        ]
                                    } for num in item["wards"]
                                ]
                            }
                        ) for item in child
                    ]
                else:
                    contact["child"] = [transform_locations(item  | {"type": location["child_type"]}) for item in child]
            else:
                contact["child"] = [transform_locations(item) for item in child]
        else:
            contact["child"] = transform_locations(child)

    return contact

def push_locations(locations: dict, parent: Optional[dict] = None) -> None:
    child = None

    if "child" in locations:
        child = locations["child"]
        del locations["child"]
    
    if parent:
        locations["parent"] = parent

    id = post(couch_url, locations)["id"]

    output_file = getenv("LOCATION_OUTPUT_FILE")
    with open(output_file, "a", encoding="utf-8") as loc:
        code = "null" if "place_code" not in locations else locations['place_code']
        loc.write(f"{locations['name']}, {code}, {id}, {locations['contact_type']} \n")
    
    if locations["contact_type"] == "c80_household":
        household_file = getenv("HOUSEHOLD_INPUT_FILE")
        with open(household_file, "a", encoding="utf-8") as hh:
            hh.write(f"{locations['hhID']}, {id} \n")
    
    if locations["contact_type"] == "c80_household_contact":
        print(locations)
        contacts_file = getenv("CONTACTS_FILE")
        with open(contacts_file, "a", encoding="utf-8") as con:
            con.write(f"{locations['parent_code']}, {id} \n")

    parent = parentize(id, parent)

    if child is None:
        return
    elif type(child) == list:
        [ push_locations(item, parent) for item in child ]
    else:
        push_locations(child, parent)

def push_users() -> None:
    household_input_file = getenv("HOUSEHOLD_INPUT_FILE")
    household_output_file = getenv("HOUSEHOLD_OUTPUT_FILE")
    with open(household_input_file, "r", encoding="utf-8") as hh_input, \
        open(household_output_file, "a", encoding="utf-8") as hh_output:
        hh_reader = csv.reader(hh_input, delimiter=",")
        for idx, row in enumerate(hh_reader):
            hh_contact = {
                "password": get_password(),
                "username": row[0].strip().lower(),
                "type": "chw",
                "place":  row[1].strip(),
                "contact": search_contact(row[0].strip())
            }

            try:
                id = post(cht_url, hh_contact)['user']['id']
                hh_output.write(f"{idx + 1}, {id}, {hh_contact['username']}, {hh_contact['password']} \n")
            except:
                print("Retrying...")
                hh_contact["password"] = get_password()

                try:
                    id = post(cht_url, hh_contact)['user']['id']
                    hh_output.write(f"{idx + 1}, {id}, {hh_contact['username']}, {hh_contact['password']} \n")
                except:
                    print(f"Error occured while creating user for contact: {row[0]} {hh_contact['username']} {hh_contact['password']}")

def run():
    input_file = getenv("LOCATION_INPUT_FILE")
    push_locations(transform_locations(load_locations(input_file)))
    push_users()