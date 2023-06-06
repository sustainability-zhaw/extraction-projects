import json
import datetime
import requests
import settings
from logger import logger
import db
import codecs


def fetch_all_projects():
    response = requests.get("https://forschungsapp-api.zhaw.ch/api/pdb/" + settings.PROJECT_DB_API_KEY)
    response.raise_for_status()
    # API Response contains UTF-8 BOM
    return json.loads(codecs.decode(response.text.encode(), 'utf-8-sig'))["data"]["pdblist"]


def map_keywords(project, info_object):
    if not "fdbwakeyword" in project:
        return
    
    field_type = type(project["fdbwakeyword"])
    keywords = []

    if field_type is dict:
        keywords.append(project["fdbwakeyword"]["fdbkeyword"])
    elif field_type is list:
        keywords.extend(item["fdbkeyword"] for item in project["fdbwakeyword"])

    if len(keywords):
        info_object["keywords"] = [{ "name": keyword } for keyword in keywords]


def map_class(project, info_boject):
    if not "fdbwathemenbereichhauptklasse" in project:
        return
    
    field_type = type(project["fdbwathemenbereichhauptklasse"])
    ddcs = []
    
    if field_type is dict and type(project["fdbwathemenbereichhauptklasse"]["fdbthemenbereichhauptklasse"]) is str:
        ddcs.append(project["fdbwathemenbereichhauptklasse"]["fdbthemenbereichhauptklasse"])
    elif field_type is list:
        ddcs.extend(item["fdbthemenbereichhauptklasse"] for item in project["fdbwathemenbereichhauptklasse"])

    if len(ddcs):
        ddcs = [ddc.split("-", 1) for ddc in ddcs]
        info_boject["class"] = [{ "id": ddc.strip(), "name": label.strip() } for ddc, label in ddcs]


def map_authors(project, info_object):
    members = []
    
    if "fdbwaprojektteamintern" in project:
        members.extend({"surname": member["lastname"], "given_name": member["firstname"] } for member in project["fdbwaprojektteamintern"])
    
    if len(members):
        info_object["authors"] = [ { "fullname": f"{member['surname']}, {member['given_name']}" } for member in members]


def run(channel):
    for project in fetch_all_projects():
        info_object = {}

        try:
            info_object["link"] = f"https://www.zhaw.ch/de/forschung/forschungsdatenbank/projektdetail/projektid/{project['fdbid']}"
            info_object["title"] = project["fdbprojekttitelde"]
            info_object["abstract"] = project["fdbprojektbeschreibungde"]
            info_object["year"] = int(project["fdbprojektstart"][0:4])
            info_object["category"] = { "name": "projects" }
            info_object["subtype"] = { "name": project["fdbprojekttyp"] }
            info_object["language"] = "de"
            info_object["dateUpdate"] = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

            if "fdbbeteiligtedepartemente" in project:
                info_object["departments"] = [{ "id": "department_" + dep.strip() } for dep in project["fdbbeteiligtedepartemente"].split(";")]

            map_keywords(project, info_object)
            map_class(project, info_object)
            map_authors(project, info_object)
        except:
            logger.exception(f"Failed to parse project: {project['link']}")
            continue

        try:
            db.upsert_info_object(info_object)
        except:
            logger.exception(f"Failed to upsert info_object: {info_object['link']}")
            continue

        try:
            channel.basic_publish(
                exchange=settings.MQ_EXCHANGE,
                routing_key="importer.object", 
                body=json.dumps({ "link": info_object["link"] })
            )
        except:
            logger.exception(f"Failed to publish import event for: {info_object['link']}")
            continue
