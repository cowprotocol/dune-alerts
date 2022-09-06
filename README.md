# Query Monitor / Dune Alerts

This package combines both [DuneAPI](https://pypi.org/project/duneapi/)
and [SlackClient](https://pypi.org/project/slackclient/) in a way that can send alerts
in slack based on dune query
results.

To run this monitoring system will require the following steps:

1. An account on [Dune Analytics](https://dune.com) and
   a [query](https://dune.com/queries/857522) you would like to
   monitor.
2. An existing slack bot ([Create a Slack App](https://api.slack.com/apps))

To run the query monitor (for a single query) you will need to provide Dune credentials
and Slack app details.
Namely, the environment variables supplied in the [sample env file](.env.sample).

## Query Monitor from Configuration

Query Monitor objects are loaded from a yaml configuration file taking the following
form:

```yaml
name: Name of your Query
id: DUNE_QUERY_ID
window: (This is Optional)
  offset: how far in hours back in time from datetime.now()
  length: time interval length
parameters:
  - key: param1
    type: number
    value: 100
  - key: param2
    type: text
    value: example
```

where `DUNE_QUERY_ID` is found in the url of your existing query.
Concretely, it is the integer at the end of this url https://dune.com/queries/857522.

For more examples on query parameter configuration, checkout our test
examples [./tests/data](./tests/data/)

With all the configuration in place, then you can run the alerter with

```shell
python -m src.slackbot --query-config QUERY_CONFIG_PATH
```

where `QUERY_CONFIG_PATH` is a filepath to the yaml file containing your query
configuration.

This will load the query details, refresh the query with given parameters, fetch the
results and send an alert to the
configured Slack channel if warranted.

## Run with Docker

From the root of this project, assuming you have a .env file with dune and slack
credentials and a query
configuration `config.yaml`

```shell
# build
docker build -t slackbot .
docker run -v ${PWD}/config.yaml:/app/config.yaml --env-file .env slackbot --query-config config.yaml
```