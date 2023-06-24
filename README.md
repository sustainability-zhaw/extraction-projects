# Extraction pipeline for project database

Imports projects from the ZHAW project database.

*Note: The project database API is only accessible from within the ZHAW network. A VPN connection is required to access it from outside.*

## Configuration

The following can be configured with environment variables or by providing a JSON file at `/etc/app/config.json`.
An additional JSON file is read from `/etc/app/secrets.json` that can be used for sensitive information.

*Note: Config files take precedence over environment variables.*

- `PROJECT_DB_API_KEY` - API Key for the ZHAW project database.
- `DB_HOST` - GraphQL host. Defaults to `localhost:8080`.
- `IMPORT_INTERVAL` - Time in seconds between fetching projects. Defualts to `86400` (24h).
- `BATCH_SIZE` - Process the fetched project list in batches. Defaults to `100`. Zero or negative value disables batching.
- `BATCH_INTERVAL` - Time in seconds to wait before processing the next batch. Defaults to `300` (5 min). Ignored if batch size is zero or negative value.
- `MQ_HOST` - RabbitMQ host. Defaults to `mq`.
- `MQ_EXCHANGE` - RabbitMQ exchange name, Defaults to `zhaw-km`.
- `MQ_HEARTBEAT` - RabbitMQ heart beat in seconds. Defaults to `6000` (1.6h).
- `MQ_TIMEOUT` - RabbitMQ blocking timeout in seconds. Defaults to `3600` (1h).
- `LOG_LEVEL` - Log level for tracing and debugging. Defaults to `ERROR`.
