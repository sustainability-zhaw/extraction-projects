import json
import datetime
import codecs
import html
import requests
import settings
import utils
from logger import logger
import db
import time


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


def run(channel):
    projects = fetch_all_projects()

    for projects_batch in utils.batch(projects, settings.BATCH_SIZE):
        logger.info("start processing batch")
        for project in projects_batch:
            info_object = {}

            try:
                info_object["link"] = f"https://www.zhaw.ch/de/forschung/forschungsdatenbank/projektdetail/projektid/{project['fdbid']}"
                info_object["abstract"] = project["fdbprojektbeschreibungde"]
                info_object["year"] = int(project["fdbprojektstart"][0:4])
                info_object["category"] = { "name": "projects" }
                info_object["subtype"] = { "name": project["fdbprojekttyp"] }
                info_object["language"] = "de"
                info_object["dateUpdate"] = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
                info_object['start_date'] = datetime.datetime.strptime(project["fdbprojektstart"].split()[0], "%Y-%m-%d").isoformat()
                info_object['end_date'] = datetime.datetime.strptime(project["fdbprojektende"].split()[0], "%Y-%m-%d").isoformat()

                info_object["title"] = project["fdbprojekttitelde"]
                if "fdbprojektuntertitelde" in project:
                    info_object["title"] += ", " + project["fdbprojektuntertitelde"]

                if "fdbbeteiligtedepartemente" in project:
                    info_object["departments"] = [{ "id": "department_" + dep.strip() } for dep in project["fdbbeteiligtedepartemente"].split(";")]

                if "fdbwaprojektteamintern" in project:
                    info_object["authors"] = list([
                        {
                            "fullname": f"{html.unescape(member['lastname'])}, {html.unescape(member['firstname'])}" 
                        } 
                        for member in project["fdbwaprojektteamintern"]
                    ])

                map_keywords(project, info_object)
                map_class(project, info_object)
            except:
                logger.exception(f"Failed to parse project: {project['fdbid']}")
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

        logger.info("finished processing batch")
        time.sleep(settings.BATCH_INTERVAL)
