#!/usr/bin/env python
"""AxonBot shell script entry point."""
import logging
import os
import sys

import dotenv

import machine
import machine.settings
import machine.core
import machine.singletons

# docs URL for setting up variables required for connecting to Axonius
AX_SETUP_URL = "https://github.com/Axonius/axonbot/blob/master/docs/axonius_setup.md"

# docs URL for setting up variables required for connecting to Slack
SLACK_SETUP_URL = "https://github.com/Axonius/axonbot/blob/master/docs/slack_setup.md"

# Variables required for axonbot to run
REQUIRED_VARIABLES = {
    "AX_KEY": AX_SETUP_URL,
    "AX_SECRET": AX_SETUP_URL,
    "AX_URL": AX_SETUP_URL,
    "SLACK_API_TOKEN": SLACK_SETUP_URL,
}


def main():
    """Main entry point."""
    dotenv.load_dotenv()

    for var, url in REQUIRED_VARIABLES.items():
        if not os.environ.get(var):
            err = "You must set {var} in .env or in your shell! See:\n{url}"
            err = err.format(var=var, url=url)
            machine.utils.text.error(err)
            sys.exit(1)

    SETTINGS = {}

    # required, Axonius API key, see: https://github.com/Axonius/axonbot/blob/master/docs/axonius_setup.md  # noqa
    SETTINGS["AX_KEY"] = os.environ["AX_KEY"]

    # required, Axonius API secret, see: https://github.com/Axonius/axonbot/blob/master/docs/axonius_setup.md  # noqa
    SETTINGS["AX_SECRET"] = os.environ["AX_SECRET"]

    # required, Axonius API url, see: https://github.com/Axonius/axonbot/blob/master/docs/axonius_setup.md  # noqa
    SETTINGS["AX_URL"] = os.environ["AX_URL"]

    # required, Slack API token, see: https://github.com/Axonius/axonbot/blob/master/docs/slack_setup.md  # noqa
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
    # slackclient is an abuser of logging.LEVEL which goes to the root logger
    # bad slackclient. bad!
    logging.getLogger(machine.__name__).setLevel(SETTINGS["MACHINE_LOGLEVEL"])
    logging.getLogger("apscheduler.scheduler").setLevel(SETTINGS["MACHINE_LOGLEVEL"])

    bot = machine.Machine()

    try:
        bot.run()
    except KeyboardInterrupt:
        machine.utils.text.announce("Goodbye!")


if __name__ == "__main__":
    main()
