<!-- MarkdownTOC -->

- [axonbot](#axonbot)
    - [Install from pip or pipenv](#install-from-pip-or-pipenv)
    - [Install from this repository](#install-from-this-repository)
    - [Architecture](#architecture)
    - [Setup a Slack Bot and get a Slack API Token](#setup-a-slack-bot-and-get-a-slack-api-token)
    - [Get the Axonius API Key and Secret for a given user](#get-the-axonius-api-key-and-secret-for-a-given-user)
    - [Running AxonBot](#running-axonbot)
        - [Prerequisites](#prerequisites)
        - [Required variables](#required-variables)
        - [Optional variables](#optional-variables)
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

## Architecture

AxonBot was written in a way that allows it to access an on-premise Axonius instance while also being able to access the Slack API via outbound access only. This prevents the need to open firewall rules and mappings inbound to AxonBot to allow Slack to reach it.

Unfortunately, this architecture makes getting a Slack API Token a bit tedius. Read on for how to do this.

## Setup a Slack Bot and get a Slack API Token

[Slack Bot Setup Instructions](docs/slack_setup.md)

## Get the Axonius API Key and Secret for a given user

[Axonius API Key and API Secret Instructions](docs/axonius_setup.md)

## Running AxonBot

### Prerequisites

The system you run AxonBot needs to be able to access the Slack API outbound only, or it needs access to a proxy that can reach the Slack API (configurable via the environment variable HTTPS_PROXY). The URL used to access the Slack API is [https://slack.com](https://slack.com).

The system you run AxonBot needs to be able to access the Axonius instance outbound only, or it needs access to a proxy that can reach the Axonius instance (configurable via the environment variable AX_HTTPS_PROXY).

### Required variables

You can set the following environment variables in your shell:

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

Or you can edit the .env file and set the same variables:

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

### Optional variables

If you need to use a proxy to connect to the internet, you can set HTTPS_PROXY in your shell or in your .env file.

If you need to use a proxy to connect to your Axonius instance, you can set AX_HTTPS_PROXY in your shell or in your .env file.

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
