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

SCRIPT_PATH_FULL = pathlib.Path(sys.argv[0]).absolute().resolve()
SCRIPT_NAME = SCRIPT_PATH_FULL.name
SCRIPT_PATH = SCRIPT_PATH_FULL.parent
PARENT_PATH = SCRIPT_PATH.parent
CWD_PATH = pathlib.Path(os.getcwd())
DEFAULT_ENV = CWD_PATH / ".env"
DEFAULT_ENV = os.environ.get("AX_DOTENV", DEFAULT_ENV) or DEFAULT_ENV
sys.path.insert(0, format(PARENT_PATH))

try:
    from axonbot.version import __version__  # noqa
except Exception:
    __version__ = "?"


def style_bold(txt, fg):
    """Style text with a bold color."""
    return click.style(txt, fg=fg, bold=True)


def style(txt, fg):
    """Style text with a non-bold color."""
    return click.style(txt, fg=fg, bold=False)


# docs URL for connecting to Axonius
AX_SETUP_URL = "https://git.io/fjyAT"

# docs URL for connecting to Slack
SLACK_SETUP_URL = "https://git.io/fjyAU"

# docs URL for proxy variables
PROXY_URL = "https://bit.ly/32TToJc"

VARINFOS = [
    {
        "var": "SLACK_API_TOKEN",
        "desc": "API Token of bot user in Slack",
        "url": SLACK_SETUP_URL,
        "req": True,
        "default_value": None,
    },
    {
        "var": "AX_URL",
        "desc": "URL of Axonius instance to connect to",
        "url": AX_SETUP_URL,
        "req": True,
        "default_value": None,
    },
    {
        "var": "AX_KEY",
        "desc": "API Key of Axonius user at AX_URL instance",
        "url": AX_SETUP_URL,
        "req": True,
        "default_value": None,
    },
    {
        "var": "AX_SECRET",
        "desc": "API Secret of Axonius user at AX_URL instance",
        "url": AX_SETUP_URL,
        "req": True,
        "default_value": None,
    },
    {
        "var": "HTTPS_PROXY",
        "desc": "Proxy to use when connecting to the Slack API",
        "url": PROXY_URL,
        "req": False,
        "default_value": "",
    },
    {
        "var": "AX_HTTPS_PROXY",
        "desc": "Proxy to use when connecting to the Axonius instance",
        "url": PROXY_URL,
        "req": False,
        "default_value": "",
    },
]

DOT_VAR_TMPL = """
# {var}=""
#   Required: {req}
#   Default value: {default_value}
#   Description: {desc}
#   Documentation URL: {url}
""".format

PROMPT_VAR_TMPL = """
    Variable: {var_color}
    Current value: {current_value}
    Default value: {default_value}
    Required: {req}
    Description: {desc_color}
    Documentation URL: {url_color}
Enter value for '{var_color}'""".format

LOAD_VAR_TMPL = "{case} '{var_color}': {desc_color}: {url_color}".format

DOT_TMPL = "# AXONBOT .env file"

for varinfo in VARINFOS:
    varinfo["var_color"] = style_bold(varinfo["var"], "blue")
    varinfo["desc_color"] = style_bold(varinfo["desc"], "green")
    varinfo["url_color"] = style_bold(varinfo["url"], "cyan")
    DOT_TMPL += DOT_VAR_TMPL(**varinfo)


def dotenv_check(ctx, create=True, mode=0o600):
    """Check if .env file supplied exists, create if not."""
    if ctx.obj.get("checked", False):
        return

    if not ctx.obj["path"].is_file():
        if create:
            ctx.obj["path"].touch(mode=mode)
            ctx.obj["path"].write_text(DOT_TMPL)
            result = style("Created new", "yellow")
        else:
            result = style("Unable to find", "red")
    else:
        result = style("Found pre-existing", "green")

    click.echo("{result} {at}".format(result=result, **ctx.obj))
    ctx.obj["checked"] = True


def prompt_var(ctx, varinfo):
    """Prompt for a variable."""
    dotenv_check(ctx)
    dotenv.load_dotenv(ctx.obj["str"])

    varinfo["current_value"] = os.environ.get(varinfo["var"], "")
    varinfo["prompt_default"] = varinfo["current_value"] or varinfo["default_value"]
    varinfo["prompt_text"] = PROMPT_VAR_TMPL(**varinfo)
    varinfo["new_value"] = click.prompt(
        varinfo["prompt_text"], default=varinfo["prompt_default"]
    )

    if varinfo["current_value"]:
        if varinfo["current_value"] == varinfo["new_value"]:
            varinfo["do_change"] = False
            varinfo["result"] = "Current value equals new value, did not update"
            varinfo["result_color"] = style(varinfo["result"], "green")
        else:
            varinfo["do_change"] = True
            varinfo["result"] = "Current value does not equal new value, updated"
            varinfo["result_color"] = style(varinfo["result"], "yellow")
    else:
        varinfo["do_change"] = True
        varinfo["result"] = "Current value is not set, added"
        varinfo["result_color"] = style_bold(varinfo["result"], "yellow")

    if varinfo["do_change"]:
        dotenv.set_key(ctx.obj["str"], varinfo["var"], varinfo["new_value"])

    text = "\n*** {result} variable '{var_color}' in {at}"
    text = text.format(at=ctx.obj["at"], **varinfo)
    click.echo(text)
    return varinfo


def load_vars(ctx):
    """Check that variables are set."""
    dotenv_check(ctx, create=False)
    dotenv.load_dotenv(ctx.obj["str"])

    fail = False

    for varinfo in VARINFOS:
        varinfo["rerun"] = ""
        value = os.environ.get(varinfo["var"], "")
        req = "required" if varinfo["req"] else "optional"
        if value:
            case = "Found {req} variable".format(req=req)
            case = style(case, "green")
            click.echo(LOAD_VAR_TMPL(case=case, **varinfo))
            continue

        if varinfo["var"] in os.environ:
            case = "Found empty {req} variable"
        else:
            case = "Unable to find {req} variable"

        if varinfo["req"]:
            case = style_bold(case.format(req=req), "red")
            fail = True
        else:
            case = style_bold(case.format(req=req), "yellow")

        click.echo(LOAD_VAR_TMPL(case=case, **varinfo))

    if fail:
        rerun = "!!! Run '{name} config' to set missing/empty variables"
        rerun = rerun.format(name=SCRIPT_NAME)
        rerun = style_bold(rerun, "red")
        rerun += " in " + ctx.obj["at"]
        click.echo(rerun)
        sys.exit(1)


ENV_HELP = (
    "Location of .env file, defaults to '{env}', uses CURRENT_WORKING_DIRECTOR/.env "
    "if environment variable 'AX_DOTENV' is not set and this is not supplied."
).format(env=format(DEFAULT_ENV))


@click.group()
@click.option(
    "--env", default=DEFAULT_ENV, type=click.Path(exists=False), help=ENV_HELP
)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, env):
    """Used to set, get or unset values from a .env file."""
    ctx.obj = {}
    ctx.obj["env"] = env
    ctx.obj["path"] = pathlib.Path(env).absolute().resolve()
    ctx.obj["str"] = format(ctx.obj["path"])
    ctx.obj["color"] = click.style(ctx.obj["str"], fg="blue")
    ctx.obj["at"] = ".env file at '{}'".format(ctx.obj["color"])


@cli.command()
@click.pass_context
def config(ctx):
    """Used to configure axonbot."""
    for varinfo in VARINFOS:
        prompt_var(ctx, varinfo)


@cli.command()
@click.pass_context
def run(ctx):
    """Used to run axonbot."""
    load_vars(ctx)

    SETTINGS = {}

    # required, Axonius API key
    SETTINGS["AX_KEY"] = os.environ["AX_KEY"]

    # required, Axonius API secret
    SETTINGS["AX_SECRET"] = os.environ["AX_SECRET"]

    # required, Axonius API url
    SETTINGS["AX_URL"] = os.environ["AX_URL"]

    # required, Slack API token
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
    cli()
