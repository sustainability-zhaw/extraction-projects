# Extraction pipeline for project database

Import projects from ZHAW project database.

## Development

- ### TODO

*Note: The project database API is only accessible from within the ZHAW network. A VPN connection is required to access it from outside.*


## Configuration File

The configuration file has to be anchored at `/etc/app/secrets.json`. The configuration MUST be stored in JSON-format. 

The configuration file MUST be stored as a SECRET because it contains the API key for accessing the (external) project database API. 

The file is organised as follows:

```json
{
   "PROJECT_DB_API_KEY": "foobar",
}
```

## Configuration Variables

The main service configuration is set via environment variables. 

- `IMPORT_INTERVAL` - Time in seconds to wait before fetching projects. Defualts to 86400 seconds (24 h).
- `BATCH_SIZE` - Process the fetched project list in batches of this size. Defaults to 100.
- `BATCH_INTERVAL` - Time in seconds to wait before processing the next batch. Defaults to 3600 seconds (5 min).
- `DB_HOST` - host or IP of the graphQL endpoint
- `LOG_LEVEL` - log level for tracing and debugging, default is `ERROR`