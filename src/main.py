from .QuadTree import QuadTree, Rectangle
import json
from .Company import Company
from .WebScrape import WebScrape

# def load_users(openAi: OpenAi):
#     # webscrape = WebScrape()
#     # webscrape.fetch_candidates()
#     with open(
#         "../data/proaktivna_prodaja_candidates.json", "r", encoding="utf-8"
#     ) as user_file:
#         users_data = json.load(user_file)
#
#     industry_oddelek_dict = Utils().xlsx_to_dict()
#
#     users = []
#     no_coords = []
#
#     for user_raw in users_data:
#         coordinates = None
#
#         try:
#             coordinates = user_raw["Coordinates"]
#         except KeyError:
#             pass
#
#         oddelek = "SS/HH"
#         try:
#             if "Oddelek" in user_raw.keys():
#                 oddelek = user_raw["Oddelek"]
#             elif user_raw.get("Industry"):
#                 oddelek = industry_oddelek_dict.get(
#                     user_raw["Industry"].split("-")[0].split(",")[0].lower(), oddelek
#                 )
#         except Exception as e:
#             print(f"User Oddelek --> {e}")
#             pass
#
#         user = User(
#             first_name=user_raw.get("First Name"),
#             id=user_raw.get("Candidate Id"),
#             surname=user_raw.get("Surname"),
#             birth_date=user_raw.get("Birth date"),
#             email=user_raw.get("Email"),
#             address=user_raw.get("Address"),
#             city=user_raw.get("City"),
#             izobrazba=user_raw.get("Stopnja izobrazbe"),
#             izkusnje=user_raw.get("Delovne izkušnje"),
#             oddelek=oddelek,
#             industry=user_raw.get("Industry"),
#             skills=user_raw.get("Skills"),
#             cv=user_raw.get("CV data"),
#             komentar=user_raw.get("Daktela komentar"),
#             coordinates=coordinates,
#             session=session,
#             AI=openAi,
#             get_cv=True,
#         )
#
#         if coordinates is None:
#             no_coords.append(user)
#         else:
#             users.append(user)
#
#     if len(users) == 0:
#         return []
#
#     user_data = json.dumps(users, indent=4, ensure_ascii=False, default=user_to_dict)
#
#     with open(
#         "../data/proaktivna_prodaja_candidates.json", "w", encoding="utf-8"
#     ) as job_file:
#         job_file.write(user_data)
#
#     no_coords_data = json.dumps(
#         no_coords, indent=4, ensure_ascii=False, default=user_to_dict
#     )
#
#     with open("./no_coords.json", "w", encoding="utf-8") as no_coords_file:
#         no_coords_file.write(no_coords_data)
#
#     return users, no_coords


def main():
    boundary = Rectangle(0, 0, 360, 180)
    qt = QuadTree(boundary, 4)
    webscrape = WebScrape()
    with open("../data/bizi_update.json", "r") as bizi_file:
        bizi = json.load(bizi_file)

    for key, value in bizi.items():
        name = key
        qt.insert(
            Company(
                name,
                value["pošta"],
                value["lokacija"],
                value["dejavnost skd"],
                value["Coordinates"],
                value["št. zaposlenih"],
            )
        )
    webscrape.fetch_candidates()
