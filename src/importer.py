import codecs
import datetime
import html
import json
import logging
import math
import time

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import requests

from settings import settings


logger = logging.getLogger(__name__)

graphql_client = Client(transport=RequestsHTTPTransport(url=f"http://{settings.DB_HOST}/graphql"))


def fetch_all_projects():
    response = requests.get("https://forschungsapp-api.zhaw.ch/api/pdb/" + settings.PROJECT_DB_API_KEY)
    response.raise_for_status()
    # API Response contains UTF-8 BOM
    return json.loads(codecs.decode(response.text.encode(), 'utf-8-sig'))["data"]["pdblist"]


def batch(list, batch_size):
    list_size = len(list)
    batch_size = batch_size if batch_size > 0 else list_size
    number_of_batches = math.ceil(list_size / batch_size) if batch_size > 0 else 0
    for batch_index, offset in enumerate(range(0, list_size, batch_size)):
        batch_number = batch_index + 1
        yield (
            list[offset:min(offset + batch_size, list_size)], 
            batch_number, 
            number_of_batches
        )


def parse_title(project):
    title = project["fdbprojekttitelde"]
    if "fdbprojektuntertitelde" in project:
        title += ", " + project["fdbprojektuntertitelde"]
    return title


def parse_authors(project):
    return list([
        {
            "fullname": f"{html.unescape(member['lastname'])}, {html.unescape(member['firstname'])}" 
        } 
        for member in project["fdbwaprojektteamintern"]
    ])


def parse_keywords(project):    
    field_type = type(project["fdbwakeyword"])
    keywords = []

    if field_type is dict:
        keywords.append(project["fdbwakeyword"]["fdbkeyword"])
    elif field_type is list:
        keywords.extend(item["fdbkeyword"] for item in project["fdbwakeyword"])

    return list([{ "name": keyword } for keyword in keywords])


def parse_class(project):
    field_type = type(project["fdbwathemenbereichhauptklasse"])
    ddcs = []
    
    if field_type is dict and type(project["fdbwathemenbereichhauptklasse"]["fdbthemenbereichhauptklasse"]) is str:
        ddcs.append(project["fdbwathemenbereichhauptklasse"]["fdbthemenbereichhauptklasse"])
    elif field_type is list:
        ddcs.extend(item["fdbthemenbereichhauptklasse"] for item in project["fdbwathemenbereichhauptklasse"])

    ddcs = [ddc.split("-", 1) for ddc in ddcs]
    return list([{ "id": ddc.strip(), "name": label.strip() } for ddc, label in ddcs])


def upsert_info_object(info_object):
    graphql_client.execute(
        gql(
            """
            mutation ($infoObject: [AddInfoObjectInput!]!) {
                addInfoObject(input: $infoObject, upsert: true) {
                    infoObject { 
                        link
                    }
                }
            }
            """
        ),
        variable_values={
            "infoObject": [info_object]
        }
    )


field_parsers = {
    "title": ("fdbprojekttitelde", parse_title),
    "abstract": ("fdbprojektbeschreibungde", lambda project: project["fdbprojektbeschreibungde"]),
    "year": ("fdbprojektstart", lambda project: int(project["fdbprojektstart"][0:4])),
    "subtype": ("fdbprojekttyp", lambda project: { "name": project["fdbprojekttyp"] }),
    "start_date": ("fdbprojektstart", lambda project: datetime.datetime.strptime(project["fdbprojektstart"].split()[0], "%Y-%m-%d").isoformat()),
    "end_date": ("fdbprojektende", lambda project: datetime.datetime.strptime(project["fdbprojektende"].split()[0], "%Y-%m-%d").isoformat()),
    "departments": ("fdbbeteiligtedepartemente", lambda project: [{ "id": "department_" + dep.strip() } for dep in project["fdbbeteiligtedepartemente"].split(";")]),
    "authors": ("fdbwaprojektteamintern", parse_authors),
    "keywords": ("fdbwakeyword", parse_keywords),
    "class": ("fdbwathemenbereichhauptklasse", parse_class)
}


def run(channel):
    projects = fetch_all_projects()

    for batch_of_projects, batch_number, number_of_batches in batch(projects, settings.BATCH_SIZE):
        logger.info(f"Processing batch {batch_number} of {number_of_batches}")
        for project in batch_of_projects:
            try:
                info_object = {
                    "link": f"https://www.zhaw.ch/de/forschung/forschungsdatenbank/projektdetail/projektid/{project['fdbid']}",
                    "language": "de",
                    "category": { "name": "projects" },
                    "dateUpdate": int(datetime.datetime.utcnow().timestamp())
                }

                for info_object_field_name in field_parsers:
                        project_field_name, parse_field = field_parsers[info_object_field_name]
                        if project_field_name in project:
                            info_object[info_object_field_name] = parse_field(project)

                upsert_info_object(info_object)

                channel.basic_publish(
                    exchange=settings.MQ_EXCHANGE,
                    routing_key="importer.object", 
                    body=json.dumps({ "link": info_object["link"] })
                )
            except:
                logger.exception(f"An error occured during processing of project: {project['fdbid']}")
                continue

        logger.info(f"Finished processing batch {batch_number} of {number_of_batches}")

        if batch_number < number_of_batches:
            logger.info(f"Waiting {settings.BATCH_INTERVAL} seconds before processing next batch")
            time.sleep(settings.BATCH_INTERVAL)
