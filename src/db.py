from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import settings


_client = Client(
    transport=RequestsHTTPTransport(url=f"http://{settings.DB_HOST}/graphql"),
    fetch_schema_from_transport=True
)
