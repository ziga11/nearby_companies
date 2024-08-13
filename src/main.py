from QuadTree import QuadTree, Rectangle
import math
import json
from Company import Company
from WebScrape import WebScrape
from User import User


def company_to_dict(company: Company):
    company_dict = company.__dict__.copy()
    company_dict["st. zaposlenih"] = company_dict.pop("count", None)
    company_dict.pop("x", None)
    company_dict.pop("y", None)
    return company_dict


def user_to_dict(user: User):
    user_dict = user.__dict__.copy()
    user_dict["Candidate Id"] = user_dict.pop("id", None)
    user_dict["First Name"] = user_dict.pop("first_name", None)
    user_dict["Surname"] = user_dict.pop("last_name", None)
    user_dict["Address"] = user_dict.pop("location", None)
    user_dict["Coordinates"] = user_dict.pop("coords", None)
    return user_dict


def distance_in_km_to_latitude(km):
    # 1 degree of latitude is approximately 111.32 km
    return km / 111.32


def distance_in_km_to_longitude(km, latitude):
    # Convert latitude to radians
    lat_rad = latitude * math.pi / 180.0

    # Calculate the distance corresponding to 1 degree of longitude at the given latitude
    longitude_degree_km = 111.32 * math.cos(lat_rad)

    # Return the change in longitude in degrees
    return km / longitude_degree_km


def load_users(qt: QuadTree):
    with open(
        "../data/proaktivna_prodaja_candidates.json", "r", encoding="utf-8"
    ) as user_file:
        users_data = json.load(user_file)

    users = []

    for user_raw in users_data:
        if "Coordinates" not in user_raw or user_raw["Coordinates"] is None:
            continue
        coordinates = user_raw["Coordinates"]

        user = User(
            id=user_raw.get("Candidate Id"),
            first_name=user_raw.get("First Name"),
            last_name=user_raw.get("Surname"),
            email=user_raw.get("Email"),
            location=user_raw.get("Address"),
            coords=coordinates,
        )
        users.append(user)

    user_data = json.dumps(
        users, indent=4, ensure_ascii=False, default=user_to_dict)

    with open(
        "../data/proaktivna_prodaja_candidates.json", "w", encoding="utf-8"
    ) as job_file:
        job_file.write(user_data)

    return users


def main():
    boundary = Rectangle(0, 0, 360, 180)
    qt = QuadTree(boundary, 4)
    webscrape = WebScrape()
    # webscrape.fetch_candidates()
    with open("../data/bizi_update.json", "r", encoding="utf-8") as bizi_file:
        bizi = json.load(bizi_file)

    with open("../data/places_coordinates.json", "r", encoding="utf-8") as places_file:
        places = json.load(places_file)

    users: list(User) = load_users(qt)

    for key, value in bizi.items():
        if "Coordinates" not in value:
            try:
                value["Coordinates"] = (
                    places[value["pošta"].split(" ", 1)[1].lower()]
                    if "pošta" in value
                    else None
                )
            except Exception as e:
                print(e)
                continue
        if value["Coordinates"] is None:
            continue

        qt.insert(
            Company(
                name=key,
                posta=value["pošta"],
                location=value["lokacija"] if "lokacija" in value else None,
                skd=value["dejavnost skd"] if "dejavnost skd" in value else None,
                coords=value["Coordinates"] if "Coordinates" in value else None,
                employee_count=(
                    value["št. zaposlenih"] if "št. zaposlenih" in value else None
                ),
            )
        )

    dct = {}

    for user in users:
        width = distance_in_km_to_latitude(70)
        height = distance_in_km_to_longitude(70, width)
        rect = Rectangle(user.coords[0], user.coords[1], width, height)
        found_companies = []
        qt.query(rect, found_companies)
        dct[f"{user.id} - {user.first_name} {user.last_name}"] = found_companies

    output_data = json.dumps(
        dct, indent=4, ensure_ascii=False, default=company_to_dict)
    result_file = "output.json"
    with open(result_file, "w", encoding="utf-8") as file:
        file.write(output_data)


main()
