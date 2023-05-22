from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import settings


_client = Client(
    transport=RequestsHTTPTransport(url=f"http://{settings.DB_HOST}/graphql"),
    fetch_schema_from_transport=True
)

def upsert_info_object(info_object):
    _client.execute(
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
