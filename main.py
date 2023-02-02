from typing import Optional
from client import post

import time
import json


MEDIC_URL="https://localhost/medic"
LOCATION_INPUT_FILE="locations.json"
LOCATION_OUTPUT_FILE="locations.csv"

double_digit = lambda x: f"0{x}" if len(str(x)) == 1 else str(x)

def parentize(child: str, parent: dict = None) -> dict:
    return {
        "_id": child,
        "parent": parent
    } if parent is not None else {
        "_id": child
    }

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

    if "place_code" in location:
        contact["place_code"] = location["place_code"]

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
                                        "name": f"Ward {num}", 
                                        "type": "c50_ward", 
                                        "place_code": f"{item['code']}{num}"
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

    id = post(MEDIC_URL, locations)["id"]

    with open(f"locations.qa.csv", "a", encoding="utf-8") as csv:
        code = "null" if "place_code" not in locations else locations['place_code']
        csv.write(f"{locations['name']}, {code}, {id}, {locations['contact_type']} \n")

    parent = parentize(id, parent)

    if child is None:
        return
    elif type(child) == list:
        [ push_locations(item, parent) for item in child ]
    else:
        push_locations(child, parent)

def load_locations(filename: str):
    with open(filename, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    push_locations(transform_locations(load_locations(LOCATION_INPUT_FILE)))