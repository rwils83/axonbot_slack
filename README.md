<!-- MarkdownTOC -->

- [axonbot](#axonbot)
    - [Install from pip or pipenv](#install-from-pip-or-pipenv)
    - [Install from this repository](#install-from-this-repository)
    - [Setup Slack Bot and get a Slack API Token](#setup-slack-bot-and-get-a-slack-api-token)
    - [Get the Axonius API Key and Secret for a given user](#get-the-axonius-api-key-and-secret-for-a-given-user)
    - [Running AxonBot](#running-axonbot)
        - [Required variables](#required-variables)
        - [Start it up](#start-it-up)
    - [Using AxonBot](#using-axonbot)

<!-- /MarkdownTOC -->

# axonbot

## Install from pip or pipenv

This package is not listed on pypi, so you can not install it this way.

## Install from this repository

Clone this repository:

```
git clone git@github.com:Axonius/axonbot.git
```

Then to setup the virtual environment:

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

Or you can edit .env and set the same variables instead of setting them on the command line:

```
# URL of the Axonius instance
AX_URL="https://axonius.server"

# API key of a user in Axonius
AX_KEY="KEY"

# API secret of a user in Axonius
AX_SECRET="SECRET"

# Slack API Token for a Slack App installed in your workspace
SLACK_API_TOKEN="TOKEN"
```

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
