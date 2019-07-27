#!/usr/bin/env python
"""AxonBot shell script entry point."""
import logging
import os
import sys
import pathlib

import click
import dotenv

import machine
import machine.settings
import machine.core
import machine.singletons

# from axonbot.version import __version__
__version__ = "1.0.2"

# docs URL for connecting to Axonius
AX_SETUP_URL = "https://github.com/Axonius/axonbot/blob/master/docs/axonius_setup.md"

# docs URL for connecting to Slack
SLACK_SETUP_URL = "https://github.com/Axonius/axonbot/blob/master/docs/slack_setup.md"

# Variables required for axonbot to run
REQUIRED_VARIABLES = {
    "SLACK_API_TOKEN": {
        "desc": "API Token of bot user in Slack",
        "doc_url": SLACK_SETUP_URL,
    },
    "AX_URL": {
        "desc": "URL of Axonius instance to connect to",
        "doc_url": AX_SETUP_URL,
    },
    "AX_KEY": {
        "desc": "API Key of Axonius user at AX_URL instance",
        "doc_url": AX_SETUP_URL,
    },
    "AX_SECRET": {
        "desc": "API Secret of Axonius user at AX_URL instance",
        "doc_url": AX_SETUP_URL,
    },
}


@click.group()
@click.option(
    "-f",
    "--file",
    default=os.path.join(os.getcwd(), ".env"),
    type=click.Path(exists=True),
    help=(
        "Location of the .env file, defaults to .env file in current working directory."
    ),
)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, file):
    """Used to set, get or unset values from a .env file."""
    ctx.obj = {}
    ctx.obj["FILE"] = file


def green(t, b=True):
    """Pass."""
    return click.style(t, fg="green", bold=b)


def red(t, b=True):
    """Pass."""
    return click.style(t, fg="red", bold=b)


def blue(t, b=True):
    """Pass."""
    return click.style(t, fg="blue", bold=b)


def prompt_var(dotenv_path, var, desc, doc_url):
    """Pass."""
    old_value = dotenv.main.DotEnv(dotenv_path=dotenv_path).get(var) or None
    text_lines = [
        "",
        "{}: {}".format(green("Description"), blue(desc)),
        "{}: {}".format(green("Docs URL"), blue(doc_url)),
        "{} '{}'".format(green("Provide"), red(var)),
    ]
    new_value = click.prompt(text="\n".join(text_lines), default=old_value)
    if old_value == new_value:
        change = "left unchanged"
    else:
        change = "updated"
        dotenv.set_key(dotenv_path, var, new_value)
    text = "'{var}' {change} in '{dotenv}'"
    text = text.format(dotenv=blue(format(dotenv_path)), var=red(var), change=change)
    click.echo(text)


@cli.command()
@click.pass_context
def config(ctx):
    """Used to configure axonbot."""
    dotenv_path = ctx.obj["FILE"]
    for var, varinfo in REQUIRED_VARIABLES.items():
        prompt_var(dotenv_path, var, varinfo["desc"], varinfo["doc_url"])


@cli.command()
@click.pass_context
def run(ctx):
    """Used to run axonbot."""
    dotenv_path = ctx.obj["FILE"]
    dotenv.load_dotenv(dotenv_path)

    for var, varinfo in REQUIRED_VARIABLES.items():
        if os.environ.get(var):
            text = "{}: '{}'"
            text = text.format(green("Found variable"), red(var))
            click.echo(text)
        else:
            prompt_var(dotenv_path, var, varinfo["desc"], varinfo["doc_url"])

    SETTINGS = {}

    # required, Axonius API key
    # see: https://github.com/Axonius/axonbot/blob/master/docs/axonius_setup.md
    SETTINGS["AX_KEY"] = os.environ["AX_KEY"]

    # required, Axonius API secret
    # see: https://github.com/Axonius/axonbot/blob/master/docs/axonius_setup.md
    SETTINGS["AX_SECRET"] = os.environ["AX_SECRET"]

    # required, Axonius API url
    # see: https://github.com/Axonius/axonbot/blob/master/docs/axonius_setup.md
    SETTINGS["AX_URL"] = os.environ["AX_URL"]

    # required, Slack API token
    # see: https://github.com/Axonius/axonbot/blob/master/docs/slack_setup.md
    SETTINGS["SLACK_API_TOKEN"] = os.environ["SLACK_API_TOKEN"]

    # optional, logging level for axonius_api_client
    SETTINGS["AX_LOGLEVEL"] = getattr(
        logging, os.environ.get("AX_LOGLEVEL", "info").upper()
    )

    # optional, logging level for slack-machine
    SETTINGS["MACHINE_LOGLEVEL"] = getattr(
        logging, os.environ.get("MACHINE_LOGLEVEL", "error").upper()
    )

    # optional, logging level for entire logging system
    SETTINGS["LOGLEVEL"] = getattr(logging, os.environ.get("LOGLEVEL", "info").upper())

    # optional, http proxy to use to connect to slack API
    SETTINGS["HTTP_PROXY"] = os.environ.get("SLACK_HTTP_PROXY", "")

    # optional, https proxy to use to connect to slack API
    SETTINGS["HTTPS_PROXY"] = os.environ.get("SLACK_HTTPS_PROXY", "")

    # optional, http proxy to use to connect to axonius API
    SETTINGS["AX_HTTP_PROXY"] = os.environ.get("AX_HTTP_PROXY", "")

    # optional, https proxy to use to connect to axonius API
    SETTINGS["AX_HTTPS_PROXY"] = os.environ.get("AX_HTTPS_PROXY", "")

    # optional, override axonbot.axonbot.AX_USER_FIELDS
    SETTINGS["AX_USER_FIELDS"] = {
        "generic": [
            "labels",
            "specific_data.data.username",
            "specific_data.data.last_seen",
            "specific_data.data.mail",
        ]
    }

    # optional, override axonbot.axonbot.AX_DEVICE_FIELDS
    SETTINGS["AX_DEVICE_FIELDS"] = {
        "generic": [
            "labels",
            "specific_data.data.hostname",
            "specific_data.data.network_interfaces",
            "specific_data.data.last_seen",
        ]
    }

    # do not change me, required settings for axonbot to work
    SETTINGS["STORAGE_BACKEND"] = "machine.storage.backends.memory.MemoryStorage"
    SETTINGS["PLUGINS"] = ["axonbot.AxonBot", "machine.plugins.builtin.help.HelpPlugin"]
    SETTINGS["DISABLE_HTTP"] = True
    SETTINGS["KEEP_ALIVE"] = 15

    def import_settings(**kwargs):
        """Monkey patcher for machine.settings.import_settings."""
        return machine.settings.CaseInsensitiveDict(SETTINGS), True

    # I do not like the import logic behind local_settings.py - lets replace it
    machine.settings.import_settings = import_settings
    machine.core.import_settings = import_settings
    machine.singletons.import_settings = import_settings

    # set the slack-machine logger levels to MACHINE_LOG
    # this does not catch everything as slackclient is an abuser of
    # logging.LEVEL which goes to the root logger - bad slackclient. bad!
    logging.getLogger(machine.__name__).setLevel(SETTINGS["MACHINE_LOGLEVEL"])
    logging.getLogger("apscheduler.scheduler").setLevel(SETTINGS["MACHINE_LOGLEVEL"])

    bot = machine.Machine()

    try:
        bot.run()
    except KeyboardInterrupt:
        machine.utils.text.announce("Goodbye!")


if __name__ == "__main__":
    this_script = pathlib.Path(sys.argv[0]).absolute().resolve()
    parent_path = this_script.parent.parent
    sys.path.insert(0, format(parent_path))
    from axonbot.version import __version__

    cli()
