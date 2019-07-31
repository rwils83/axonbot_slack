#!/usr/bin/env python
"""axonbot_slack shell script entry point."""
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
import slackclient

SCRIPT_PATH_FULL = pathlib.Path(sys.argv[0]).absolute().resolve()
SCRIPT_NAME = SCRIPT_PATH_FULL.name
SCRIPT_PATH = SCRIPT_PATH_FULL.parent
PARENT_PATH = SCRIPT_PATH.parent
CWD_PATH = pathlib.Path(os.getcwd())
DEFAULT_ENV = CWD_PATH / ".env"
DEFAULT_ENV = os.environ.get("AX_DOTENV", DEFAULT_ENV) or DEFAULT_ENV
sys.path.insert(0, format(PARENT_PATH))

import axonbot_slack  # noqa


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

USER_FIELDS = "generic:labels,username,last_seen,mail"
DEVICE_FIELDS = "generic:labels,hostname,network_interfaces,last_seen"

VARINFOS = [
    {
        "var": "SLACK_API_TOKEN",
        "desc": "API Token of bot user in Slack",
        "url": SLACK_SETUP_URL,
        "req": True,
        "default_value": None,
        "hidden": True,
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
        "hidden": True,
    },
    {
        "var": "AX_SECRET",
        "desc": "API Secret of Axonius user at AX_URL instance",
        "url": AX_SETUP_URL,
        "req": True,
        "default_value": None,
        "hidden": True,
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
    {
        "var": "AX_DEVICE_FIELDS",
        "desc": "Default fields to return in device responses",
        "url": "TODO",
        "req": False,
        "default_value": DEVICE_FIELDS,
    },
    {
        "var": "AX_USER_FIELDS",
        "desc": "Default fields to return in user responses",
        "url": "TODO",
        "req": False,
        "default_value": USER_FIELDS,
    },
    {
        "var": "LOGLEVEL",
        "desc": "Logging level to use for all logging",
        "url": "TODO",
        "req": False,
        "default_value": "info",
        "check": "loglevel",
    },
    {
        "var": "AX_LOGLEVEL",
        "desc": "Logging level to use for Axonius API logging",
        "url": "TODO",
        "req": False,
        "default_value": "info",
        "check": "loglevel",
    },
]

DOT_VAR_TMPL = """
# {var}=""
#   Required: {req}
#   Default value: {default_value!r}
#   Description: {desc}
#   Documentation URL: {url}
""".format

PROMPT_VAR_TMPL = """
    Variable: {var_color}
    Current value: {current_value!r}
    Default value: {default_value!r}
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


class HiddenValue(object):
    """Pass."""

    def __init__(self, value=""):
        """Pass."""
        self.value = value

    def __str__(self):
        """Pass."""
        return "*" * len(self.value or "")

    def __repr__(self):
        """Pass."""
        return "*" * len(self.value or "")


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

    hidden = varinfo.get("hidden", False)
    current_value = os.environ.get(varinfo["var"], "")
    default_value = current_value or varinfo["default_value"]

    prompt_default = default_value
    varinfo["current_value"] = current_value

    if hidden:
        if default_value:
            prompt_default = HiddenValue(default_value)
        if current_value:
            varinfo["current_value"] = HiddenValue(current_value)

    new_value = click.prompt(
        PROMPT_VAR_TMPL(**varinfo), default=prompt_default, hide_input=hidden
    )

    if isinstance(new_value, HiddenValue):
        new_value = new_value.value

    if current_value:
        if current_value == new_value:
            do_change = False
            result = "Current value equals new value, did not update variable"
            result = style(result, "green")
        else:
            do_change = True
            result = "Current value does not equal new value, updated variable"
            result = style(result, "yellow")
    else:
        do_change = True
        result = "Current value is not set, added variable"
        result = style_bold(result, "yellow")

    if do_change:
        dotenv.set_key(ctx.obj["str"], varinfo["var"], new_value)

    text = "\n*** {result} '{var_color}' in {at}"
    text = text.format(at=ctx.obj["at"], result=result, **varinfo)
    click.echo(text)
    return varinfo


def get_loglvl(lvl, var):
    """Pass."""
    try:
        lvl = getattr(logging, lvl.upper())
    except Exception:
        lvls = ["debug", "info", "warning", "error", "fatal"]
        text = "Invalid logging level {lvl} in variable {var}, valid levels: {valid}"
        text = text.format(lvl=lvl, var=var, valid=", ".join(lvls))
        click.echo(style_bold(text, "red"))
        sys.exit(1)
    return lvl


def patch_import_settings(settings):
    """Replace import logic in machine."""
    # I do not like the import logic behind local_settings.py - lets replace it
    def import_settings(**kwargs):
        """Monkey patcher for machine.settings.import_settings."""
        return machine.settings.CaseInsensitiveDict(settings), True

    machine.settings.import_settings = import_settings
    machine.core.import_settings = import_settings
    machine.singletons.import_settings = import_settings


def check_var(varinfo, value):
    """Pass."""
    check = varinfo.get("check", "")
    if check == "loglevel":
        value = get_loglvl(lvl=value, var=varinfo["var"])
    return value


def load_settings(ctx):
    """Check that variables are set."""
    dotenv_check(ctx, create=False)
    dotenv.load_dotenv(ctx.obj["str"])

    settings = {}

    fail = False

    for varinfo in VARINFOS:
        value = os.environ.get(varinfo["var"], "")

        if varinfo["req"]:
            req = "required variable"
        else:
            req = "optional variable"

        if value:
            case = "Found {req}".format(req=req)
            case = style(case, "green")
            click.echo(LOAD_VAR_TMPL(case=case, **varinfo))
            settings[varinfo["var"]] = check_var(varinfo=varinfo, value=value)
            continue

        if varinfo["var"] in os.environ:
            case = "Found empty {req}"
        else:
            case = "Unable to find {req}"

        if varinfo["req"]:
            default = ""
            case = style_bold(case.format(req=req, default=default), "red")
            fail = True
        else:
            default = " [will use default of {default_value!r}]".format(**varinfo)
            case = style_bold(case.format(req=req, default=default), "yellow")
            value = varinfo["default_value"]
            settings[varinfo["var"]] = check_var(varinfo=varinfo, value=value)

        text = LOAD_VAR_TMPL(case=case, **varinfo) + default
        click.echo(text)

    if fail:
        rerun = "!!! Run '{name} config' to set missing/empty variables"
        rerun = rerun.format(name=SCRIPT_NAME)
        rerun = style_bold(rerun, "red")
        rerun += " in " + ctx.obj["at"]
        click.echo(rerun)
        sys.exit(1)

    settings["STORAGE_BACKEND"] = "machine.storage.backends.memory.MemoryStorage"
    settings["PLUGINS"] = [
        "axonbot_slack.main.AxonBotSlack",
        "machine.plugins.builtin.help.HelpPlugin",
    ]
    settings["DISABLE_HTTP"] = True
    settings["KEEP_ALIVE"] = 15

    patch_import_settings(settings)
    return settings


ENV_HELP = (
    "Location of .env file, defaults to '{env}', uses CURRENT_WORKING_DIRECTOR/.env "
    "if environment variable 'AX_DOTENV' is not set and this is not supplied."
).format(env=format(DEFAULT_ENV))


@click.group()
@click.option(
    "--env", default=DEFAULT_ENV, type=click.Path(exists=False), help=ENV_HELP
)
@click.version_option(version=axonbot_slack.version.__version__)
@click.pass_context
def cli(ctx, env):
    """Used to configure, test, or run the Slack bot for Axonius."""
    ctx.obj = {}
    ctx.obj["env"] = env
    ctx.obj["path"] = pathlib.Path(env).absolute().resolve()
    ctx.obj["str"] = format(ctx.obj["path"])
    ctx.obj["color"] = click.style(ctx.obj["str"], fg="blue")
    ctx.obj["at"] = ".env file at '{}'".format(ctx.obj["color"])


@cli.command()
@click.pass_context
def config(ctx):
    """Used to configure axonbot_slack."""
    for varinfo in VARINFOS:
        prompt_var(ctx, varinfo)


@cli.command()
@click.pass_context
def test(ctx):
    """Used to test axonbot_slack variables."""
    settings = load_settings(ctx)
    fail = False
    try:
        ax_client = axonbot_slack.main.AxonConnection(settings=settings)
        ax_client.start()
    except axonbot_slack.main.AxonError as exc:
        text = "Unable to connect to Axonius: {msg}".format(msg=exc.msg)
        click.echo(click.style(text, "red"))
        fail = True
    except Exception as exc:
        text = "Unable to connect to Axonius: {msg}".format(msg=exc)
        click.echo(click.style(text, "red"))
        fail = True
    else:
        text = "Successfully connected to Axonius: {url}"
        text = text.format(url=ax_client.http_client.url)
        click.echo(click.style(text, "green"))

    proxies = {}

    if settings.get("HTTPS_PROXY", ""):
        proxies["https"] = settings["HTTPS_PROXY"]

    token = settings["SLACK_API_TOKEN"]

    slack_client = slackclient.SlackClient(token=token, proxies=proxies)

    try:
        slack_client.server.rtm_connect()
    except Exception as exc:
        try:
            reply = getattr(exc, "reply", "")
            reply = exc.reply.json()
        except Exception:
            reply = getattr(exc, "reply", "")

        text = "Unable to connect to Slack: {exc} {reply}"
        text = text.format(exc=exc, reply=reply)
        click.echo(click.style(text, "red"))
        fail = True
    else:
        text = "Successfully connected to Slack"
        click.echo(click.style(text, "green"))

    if fail:
        sys.exit(1)


@cli.command()
@click.pass_context
def run(ctx):
    """Used to run axonbot_slack."""
    load_settings(ctx)

    bot = machine.Machine()

    try:
        bot.run()
    except KeyboardInterrupt:
        machine.utils.text.announce("Goodbye!")


if __name__ == "__main__":
    cli()
