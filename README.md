<!-- MarkdownTOC -->

- [axonbot](#axonbot)
    - [Install](#install)
    - [Setup Slack Bot and get a Slack API Token](#setup-slack-bot-and-get-a-slack-api-token)
    - [Get the Axonius API Key and Secret for a given user](#get-the-axonius-api-key-and-secret-for-a-given-user)
    - [Running AxonBot](#running-axonbot)
        - [Required variables](#required-variables)
        - [Start it up](#start-it-up)
    - [Using AxonBot](#using-axonbot)

<!-- /MarkdownTOC -->

# axonbot

## Install
To setup the virtual environment:

```
pipenv install
```

or install the requirements to global site packages:

```
pip install -r requirements.txt
```

## Setup Slack Bot and get a Slack API Token

[Slack Bot Setup Instructions](docs/slack_setup.md)

## Get the Axonius API Key and Secret for a given user

[Axonius API Key Instructions](docs/axonius_setup.md)

## Running AxonBot

### Required variables

Either set the following environment variables:

```
# URL of the Axonius instance
export AX_URL="https://axonius.server"

# API key of a user in Axonius
export AX_KEY="KEY"

# API secret of a user in Axonius
export AX_SECRET="SECRET"

# Slack API Token for a Slack App installed in your workspace
export SLACK_API_TOKEN="TOKEN"
```

or edit local_settings.py and set the same variables

### Start it up

Inside of a pipenv:

```
pipenv run python run.py
```

Or if you installed the packages globally:

```
python run.py
```

## Using AxonBot

[Using AxonBox](docs/axonbot_using.md)
