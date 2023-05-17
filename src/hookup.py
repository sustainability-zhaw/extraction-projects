import datetime
import requests
import settings
from logger import logger
import db


def fetch_all_projects():
    response = requests.get("https://forschungsapp-api.zhaw.ch/api/pdb/" + PROJECT_DB_API_KEY)
    response.raise_for_status()
    return response.json()["data"]["pdblist"]


def run(channel, exchane):
    for project in fetch_all_projects():
        info_object = {}
        info_object["authors"] = []
        info_object["start"] = project["fdbprojektstart"][0:3]
        info_object["abstract"] = project["fdbprojektbeschreibungde"]
        info_object["language"] = "de"
        info_object["link"] = f"https://www.zhaw.ch/de/forschung/forschungsdatenbank/projektdetail/projektid/{project['fdbid']}/"
        info_object["keywords"] = [{ "name": keyword } for keyword in project["fdbkeyword"].split(",")]

        ddcs = [ddc.split("-") for ddc in project["fdbthemenbereichhauptklasse"].split(",")]
        info_object["class"] = [ { "id": ddc.strip(), "name", label.strip() } for ddc, label in ddcs ]

        info_object["departments"] = [{ name: "departement_" + dep.strip().toUpper() } for dep in project["fdbbeteiligtedepartemente"].split(";")]
        info_object["date_update"] = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

        members = [{ "id": project["fdbkurzzeichenkontaktpersonperson"], "surname": project["FDBnachnameKontaktperson"], "given_name": project["FDBvornameKontaktperson"], "function": "Kontaktperson" }]
        members.extend({ "id": memeber["shortmark"], "surname": member["lastname"], "given_name": member["firstname"], "function": member["projectfunction"] } for member in project["fdbwaprojektteamintern"])
        info_object["authors"] = [ { "fullname": f"{member['surname']}, {member['given_name']}" } for member in members]
        info_object["authororder"] = [ { "position": index, "label": member["function"] } for index, member for enumerate(members) ]

        info_object["category"] = { "name": "Project" }
        info_object["subtype"] = { "name": project["fdbprojekttyp"] }

        try:
            requests.upsert_info_object(info_object)
        except:
            logger.exception(f"Failed to upsert info_object: {info_object['link']}")
            continue

        try:
            channel.basic_publish(
                exchange=settings.MQ_EXCHANGE,
                routing_key="importer.object", 
                body={ "link": info_object["link"] }
            )
        except:
            logger.exception(f"Failed to published import event for: {info_object['link']}")
            continue
