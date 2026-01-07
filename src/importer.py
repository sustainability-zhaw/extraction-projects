import codecs
import datetime
import json
import logging
import math
import time

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import requests

from settings import settings
from new_to_old_id_map import NEW_TO_OLD_ID_MAP

logger = logging.getLogger(__name__)

# don't initialize client here, because settings are not loaded, yet
graphql_client = None

def fetch_all_project_ids():
    response = requests.get(
        url="https://api-gateway.zhaw.ch/research/v1/projects?lang=de&view=id",
        headers={ "ApiKey": settings.PROJECT_DB_API_KEY }
    )
    response.raise_for_status()
    # API Response contains UTF-8 BOM
    return list([ project["project_id"] for project in json.loads(codecs.decode(response.text.encode(), 'utf-8-sig'))["data"]["projects"]])


def fetch_project(project_id):
    response = requests.get(
        url=f"https://api-gateway.zhaw.ch/research/v1/projects/{project_id}?lang=de&view=id",
        headers={ "ApiKey": settings.PROJECT_DB_API_KEY }
    )
    response.raise_for_status()
    # API Response contains UTF-8 BOM
    return json.loads(codecs.decode(response.text.encode(), 'utf-8-sig'))["data"]["project"]


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


def upsert_info_object(info_object):
    global graphql_client

    if graphql_client is None:
        logger.info(f"connect to database at '{settings.DB_HOST}'")
        graphql_client = Client(transport=RequestsHTTPTransport(url=f"http://{settings.DB_HOST}/graphql"))
    
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
    "title": ("title", lambda project: project["title"]),
    "abstract": ("description", lambda project: project["description"]),
    "year": ("project_start", lambda project: int(project["project_start"][0:4])),
    "subtype": ("project_typ", lambda project: { "name": project["project_typ"]["name"] }),
    "start_date": ("project_start", lambda project: datetime.datetime.strptime(project["project_start"], "%Y-%m-%d").isoformat()),
    "end_date": ("project_end", lambda project: datetime.datetime.strptime(project["project_end"], "%Y-%m-%d").isoformat()),
    "departments": ("organisation_unit", lambda project: list([{ "id": "department_" + dep.upper() } for dep in { ou["code"][0] for ou in project["organisation_unit"] }])),
    "authors": ("team", lambda project: list([{ "fullname": f"{member['lastname']}, {member['firstname']}" } for member in project["team"]])),
    "keywords": ("keyword", lambda project: list([{ "name": keyword["name"] } for keyword in project["keyword"]])),
    # "class": ("fdbwathemenbereichhauptklasse", parse_class) # Does not exist anymore in new api
}


def run(channel):    
    projects_ids = fetch_all_project_ids()

    for batch_of_project_ids, batch_number, number_of_batches in batch(projects_ids, settings.BATCH_SIZE):
        logger.info(f"Processing batch {batch_number} of {number_of_batches}")
        for project_id in batch_of_project_ids:
            try:
                project = fetch_project(project_id)

                info_object = {
                    "link":  f"https://www.zhaw.ch/de/forschung/forschungsdatenbank/projektdetail/projektid/{NEW_TO_OLD_ID_MAP[project_id]}" if project_id in NEW_TO_OLD_ID_MAP else f"https://www.zhaw.ch/de/forschung/projekt/{project_id}",
                    "language": "de",
                    "category": { "name": "projects" },
                    "dateUpdate": int(datetime.datetime.utcnow().timestamp()),
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
                logger.exception(f"An error occured during processing of project: {project_id}")
                continue

        logger.info(f"Finished processing batch {batch_number} of {number_of_batches}")

        if batch_number < number_of_batches:
            logger.info(f"Waiting {settings.BATCH_INTERVAL} seconds before processing next batch")
            time.sleep(settings.BATCH_INTERVAL)
