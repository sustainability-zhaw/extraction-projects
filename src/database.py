from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


class Database:
    def __init__(self, host):
        self._client = Client(
            transport=RequestsHTTPTransport(url=f"http://{host}/graphql"),
            fetch_schema_from_transport=True
        )
