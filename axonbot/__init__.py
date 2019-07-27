"""Axonbot plugin package for slack-machine."""
import datetime
import json
import logging
import sys

import axonius_api_client

from machine.plugins import base
from machine.plugins import decorators
from machine.utils import text
from machine.slack import MessagingClient
from machine.singletons import Slack

import cachetools
import requests

from . import cli
from . import version


TTL_CACHE = cachetools.TTLCache(maxsize=512, ttl=10 * 60)

LABELS_CMD = "labels "
LABELS_SUB_CMDS = [
    {"cmd": "add ", "action": "Added", "method_name": "add_labels_by_rows"},
    {"cmd": "delete ", "action": "Deleted", "method_name": "delete_labels_by_rows"},
]
ADD_CMD = "add "
DELETE_CMD = "delete "
AX_DEVICE_FIELDS = {
    "generic": [
        "labels",
        "specific_data.data.hostname",
        "specific_data.data.network_interfaces",
        "specific_data.data.last_seen",
    ]
}
AX_USER_FIELDS = {
    "generic": [
        "labels",
        "specific_data.data.username",
        "specific_data.data.last_seen",
        "specific_data.data.mail",
    ]
}


logger = logging.getLogger(__name__)


def now():
    """Get a file friendly date string for now."""
    return datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")


def rstrip(obj, postfix):
    """Pass."""
    if isinstance(obj, (list, tuple)):
        obj = [rstrip(x, postfix) for x in obj]
    elif isinstance(obj, str):
        plen = len(postfix)
        obj = obj[:-plen] if obj.endswith(postfix) else obj
    return obj


def lstrip(obj, prefix):
    """Pass."""
    if isinstance(obj, (list, tuple)):
        obj = [lstrip(obj=x, prefix=prefix) for x in obj]
    elif isinstance(obj, str):
        plen = len(prefix)
        obj = obj[plen:] if obj.startswith(prefix) else obj
    return obj


@decorators.required_settings(["AX_URL", "AX_KEY", "AX_SECRET"])
class AxonBot(base.MachineBasePlugin):
    """Axonius Slack Bot."""

    def init(self):
        """Pass."""
        ax_log_level = self.settings.get("AX_LOGLEVEL", logging.INFO)
        logging.getLogger("axonius_api_client").setLevel(ax_log_level)

        self._http_client = axonius_api_client.http.HttpClient(
            url=self.settings["AX_URL"]
        )
        self._http_client.session.proxies = {}
        self._http_client.session.proxies["http"] = self.settings.get(
            "AX_HTTP_PROXY", ""
        )
        self._http_client.session.proxies["https"] = self.settings.get(
            "AX_HTTPS_PROXY", ""
        )
        try:
            self._auth_method = axonius_api_client.auth.AuthKey(
                http_client=self._http_client,
                key=self.settings["AX_KEY"],
                secret=self.settings["AX_SECRET"],
            )
            self._auth_method.login()
        except requests.exceptions.ConnectTimeout as exc:
            m = "Unable to connect to Axonius Instance using {client}: {exc}"
            m = m.format(client=self._http_client, exc=exc)
            text.error(m)
            sys.exit(1)

        self._api_users = axonius_api_client.api.Users(auth=self._auth_method)
        self._api_users._type = "users"
        self._api_users._get_fields = self.settings.get(
            "AX_USER_FIELDS", AX_USER_FIELDS
        )

        self._api_devices = axonius_api_client.api.Devices(auth=self._auth_method)
        self._api_devices._type = "devices"
        self._api_devices._get_fields = self.settings.get(
            "AX_DEVICE_FIELDS", AX_DEVICE_FIELDS
        )

        m = "Axonius connected: {}!"
        m = m.format(self._auth_method)
        text.announce(m)

    @decorators.respond_to(regex=r"^count device$")
    def count_device(self, msg):
        """count device: Get the count of all devices in the system."""
        count = self._api_devices.get_count()

        send_text = "Total devices: {count}"
        send_text = send_text.format(count=count)
        msg.reply(send_text, in_thread=True)

    @decorators.respond_to(regex=r"^count user$")
    def count_user(self, msg):
        """count user: Get the count of all users in the system."""
        count = self._api_users.get_count()

        send_text = "Total users: {count}"
        send_text = send_text.format(count=count)
        msg.reply(send_text, in_thread=True)

    @decorators.respond_to(regex=r"^fields user$")
    def fields_user(self, msg):
        """fields user: Show the fields that will be returned in responses."""
        send_text = self._build_get_fields_lines(api_type=self._api_users)
        msg.reply(send_text, in_thread=True)

    @decorators.respond_to(regex=r"^fields user add (?P<adapter>\S+) (?P<field>\S+)")
    def fields_user_add(self, msg, adapter, field):
        """fields user add [adapter] [field]: Add an adapters field for user responses."""  # noqa
        self._field_add(msg=msg, api_type=self._api_users, adapter=adapter, field=field)

    @decorators.respond_to(regex=r"^fields user delete (?P<adapter>\S+) (?P<field>\S+)")
    def fields_user_delete(self, msg, adapter, field):
        """fields user delete [adapter] [field]: Delete an adapters field for user responses."""  # noqa
        self._field_del(msg=msg, api_type=self._api_users, adapter=adapter, field=field)

    @decorators.respond_to(regex=r"^fields device$")
    def fields_device(self, msg):
        """fields device: Show the fields that will be returned in responses."""  # noqa
        send_text = self._build_get_fields_lines(api_type=self._api_devices)
        msg.reply(send_text, in_thread=True)

    @decorators.respond_to(regex=r"^fields device add (?P<adapter>\S+) (?P<field>\S+)")
    def fields_device_add(self, msg, adapter, field):
        """fields device add [adapter] [field]: Add an adapters field for device responses."""  # noqa
        self._field_add(
            msg=msg, api_type=self._api_devices, adapter=adapter, field=field
        )

    @decorators.respond_to(
        regex=r"^fields device delete (?P<adapter>\S+) (?P<field>\S+)"
    )
    def fields_device_delete(self, msg, adapter, field):
        """fields device delete [adapter] [field]: Delete an adapters field for device responses."""  # noqa
        self._field_del(
            msg=msg, api_type=self._api_devices, adapter=adapter, field=field
        )

    @decorators.respond_to(regex=r"^get user query ```(?P<value>.*)```")
    def user_by_query(self, msg, value):
        """get user query [value]: Get users by a query generated by Axonius, value must be fenced with triple backticks"""  # noqa
        self._fetch_query(api_type=self._api_users, query=value, msg=msg)

    @decorators.respond_to(regex=r"^get user username (?P<value>\S+)")
    def user_by_username(self, msg, value):
        """get user username [value]: Get users by username (prefix value with *re=* to use regex)"""  # noqa
        self._fetch_by(
            api_type=self._api_users,
            value_name="username",
            value=value,
            field="username",
            field_adapter="generic",
            msg=msg,
        )

    @decorators.respond_to(regex=r"^get user email (?P<value>\S+)")
    def user_by_email(self, msg, value):
        """get user email [value]: Get users by email (prefix value with *re=* to use regex)"""  # noqa
        self._fetch_by(
            api_type=self._api_users,
            value_name="email",
            value=value,
            field="mail",
            field_adapter="generic",
            msg=msg,
        )

    @decorators.respond_to(regex=r"^get device query ```(?P<value>.*)```")
    def device_by_query(self, msg, value):
        """get device query [value]: Get devices by a query generated by Axonius, value must be fenced with triple backticks"""  # noqa
        self._fetch_query(api_type=self._api_devices, query=value, msg=msg)

    @decorators.respond_to(regex=r"^saved query users (?P<value>\S.*)")
    def get_by_saved_query_users(self, msg, value):
        """saved query users [value]: Get all of the users from a saved query"""
        self._get_by_saved_query(msg=msg, api_type=self._api_users, value=value)

    @decorators.respond_to(regex=r"^saved query devices (?P<value>\S.*)")
    def get_by_saved_query_devices(self, msg, value):
        """saved query devices [value]: Get all of the devices from a saved query"""
        self._get_by_saved_query(msg=msg, api_type=self._api_devices, value=value)

    @decorators.respond_to(regex=r"^saved query devices$")
    def get_device_saved_queries(self, msg):
        """saved query devices: Get a list of all saved queries for devices"""
        self._get_saved_queries(msg=msg, api_type=self._api_devices)

    @decorators.respond_to(regex=r"^saved query users$")
    def get_user_aved_queries(self, msg):
        """saved query users: Get a list of all saved queries for users"""
        self._get_saved_queries(msg=msg, api_type=self._api_users)

    @decorators.respond_to(regex=r"^get device hostname (?P<value>\S+)")
    def device_by_hostname(self, msg, value):
        """get device hostname [value]: Get devices by hostname (prefix value with *re=* to use regex)"""  # noqa
        self._fetch_by(
            api_type=self._api_devices,
            value_name="hostname",
            value=value,
            field="hostname",
            field_adapter="generic",
            msg=msg,
        )

    @decorators.respond_to(regex=r"^get device mac (?P<value>\S+)")
    def device_by_mac(self, msg, value):
        """get device mac [value]: Get devices by MAC address (prefix value with *re=* to use regex)"""  # noqa
        self._fetch_by(
            api_type=self._api_devices,
            value_name="MAC Address",
            value=value,
            field="network_interfaces.mac",
            field_adapter="generic",
            msg=msg,
        )

    @decorators.respond_to(regex=r"^get device ip (?P<value>\S+)")
    def device_by_ip(self, msg, value):
        """get device ip [value]: Get devices by ip (prefix value with *re=* to use regex)"""  # noqa
        self._fetch_by(
            api_type=self._api_devices,
            value_name="IP Address",
            value=value,
            field="network_interfaces.ips",
            field_adapter="generic",
            msg=msg,
        )

    @decorators.process("message")
    def handle_thread(self, event):
        """Handle all messages that are in threads and not from this bot."""
        if "thread_ts" not in event:
            return
        if event["user"] == self.retrieve_bot_info()["id"]:
            return

        msg = self._gen_message(event)

        check = msg.text.lower()
        if check.startswith(LABELS_CMD):
            self._handle_labels(event, msg)
        else:
            send_text = [
                "Thread commands:",
                "\t*labels add* label1,label2,label3",
                "\t*labels delete* label1,label2,label3",
            ]
            msg.reply("\n".join(send_text), in_thread=True)

    def _handle_labels(self, event, msg):
        if msg.thread_ts not in TTL_CACHE:
            send_text = (
                "No objects requested or objects have expired, get an object first!"
            )
            msg.reply(send_text, in_thread=True)
            return

        cache_entry = TTL_CACHE[msg.thread_ts]

        cmd = lstrip(msg.text, LABELS_CMD)

        labels = ""
        label_sub_cmd = None

        for i in LABELS_SUB_CMDS:
            if cmd.lower().startswith(i["cmd"]):
                labels = lstrip(cmd, i["cmd"])
                label_sub_cmd = i
                break

        if not label_sub_cmd:
            send_text = "Missing label command, supply one of: {cmds}"
            send_text = send_text.format(
                cmds=", ".join([i["cmd"] for i in LABELS_SUB_CMDS])
            )
            msg.reply(send_text, in_thread=True)
            return

        labels = [x.strip() for x in labels.split(",") if x.strip()]
        if not labels:
            send_text = "No labels provided, provide a CSV list of labels!"
            msg.reply(send_text, in_thread=True)
            return

        change_method = getattr(cache_entry["api_type"], label_sub_cmd["method_name"])
        changed = change_method(rows=cache_entry["rows"], labels=labels)
        send_text = "{action} labels {labels!r} on {changed} {api_type}"
        send_text = send_text.format(
            action=label_sub_cmd["action"],
            labels=", ".join(labels),
            changed=changed,
            api_type=cache_entry["api_type"]._type,
        )
        msg.reply(send_text, in_thread=True)
        return

    def _gen_message(self, event):
        return base.Message(MessagingClient(), event, self._fq_name)

    def _fetch_query(self, api_type, query, msg):
        try:
            rows = list(
                api_type.get(query=query, row_count_min=1, **api_type._get_fields)
            )
        except axonius_api_client.api.exceptions.TooFewObjectsFound:
            send_text = "No {api_type} found using query {query!r}"
            send_text = send_text.format(api_type=api_type._type, query=query)
            msg.reply(send_text, in_thread=True)
        except Exception as exc:
            send_text = "Error fetching {api_type} using query {query!r}: {exc}"
            send_text = send_text.format(api_type=api_type._type, query=query, exc=exc)
            msg.reply(send_text, in_thread=True)
        else:
            TTL_CACHE[msg.thread_ts] = {"api_type": api_type, "rows": rows}
            json_rows = json.dumps(rows, indent=2)
            filename = "{api_type}_{dt}.json".format(api_type=api_type._type, dt=now())
            self._upload_file_reply(msg=msg, filename=filename, content=json_rows)

    def _fetch_by(self, api_type, value_name, value, field, field_adapter, msg):
        kwargs = {}
        kwargs.update(api_type._get_fields)
        kwargs["field"] = field
        kwargs["field_adapter"] = field_adapter
        kwargs["row_count_min"] = 1
        kwargs["row_count_max"] = None

        if value.lower().startswith("re="):
            kwargs["value"] = value[3:].strip()
            kwargs["regex"] = True
        else:
            kwargs["value"] = value.strip()
            kwargs["regex"] = False

        try:
            rows = api_type.get_by_field_value(**kwargs)
        except axonius_api_client.api.exceptions.TooFewObjectsFound:
            send_text = "No {api_type} matching {value_name} {value!r} found"
            send_text = send_text.format(
                api_type=api_type._type, value=value, value_name=value_name
            )
            msg.reply(send_text, in_thread=True)
        except Exception as exc:
            send_text = (
                "Error fetching {api_type} matching {value_name} {value!r}: {exc}"
            )
            send_text = send_text.format(
                api_type=api_type._type, value=value, value_name=value_name, exc=exc
            )
            msg.reply(send_text, in_thread=True)
        else:
            TTL_CACHE[msg.thread_ts] = {"api_type": api_type, "rows": rows}
            json_rows = json.dumps(rows, indent=2)
            filename = "{api_type}_{dt}.json".format(api_type=api_type._type, dt=now())
            self._upload_file_reply(msg=msg, filename=filename, content=json_rows)

    def _upload_file_reply(
        self,
        msg,
        filename,
        content,
        in_thread=True,
        initial_comment=None,
        filetype=None,
    ):
        kwargs = {}
        kwargs["method"] = "files.upload"
        kwargs["content"] = content
        kwargs["filename"] = filename
        kwargs["title"] = filename
        kwargs["channels"] = [msg.channel.id]
        if filetype:
            kwargs["filetype"] = filetype
        if initial_comment:
            kwargs["initial_comment"] = initial_comment
        if in_thread and msg.thread_ts:
            kwargs["thread_ts"] = msg.thread_ts
        instance = Slack.get_instance()
        response = instance.api_call(**kwargs)
        send_text = "Uploaded {filename!r} to channel {channel} in thread {thread}"
        send_text = send_text.format(
            filename=filename,
            channel=msg.channel.id,
            thread=kwargs.get("thread_ts", None),
        )
        text.announce(send_text)
        return response

    def _build_get_fields_lines(self, api_type):
        lines = ["Current fields for {api_type}:".format(api_type=api_type._type)]

        for k, v in api_type._get_fields.items():
            line = "\tAdapter: *{}*".format(k)
            lines.append(line)
            for i in v:
                line = "\t\t{}".format(i)
                lines.append(line)
            lines.append("")
        return "\n".join(lines)

    def _find_field(self, api_type, adapter, field, msg):
        try:
            known_fields = api_type.get_fields()
            if adapter != "generic":
                known_adapters = list(known_fields["specific"].keys())
                adapter = axonius_api_client.api.utils.find_adapter(
                    name=adapter, known_names=known_adapters
                )
            field = axonius_api_client.api.utils._find_field(
                name=field, adapter=adapter, fields=known_fields
            )
            return adapter, field
        except axonius_api_client.api.exceptions.UnknownAdapterName as exc:
            known_names = "\n\t" + "\n\t".join(["generic"] + exc.known_names)
            send_text = (
                "No such adapter named {adapter!r}, valid adapter names: {known_names}"
            )
            send_text = send_text.format(adapter=adapter, known_names=known_names)
            msg.reply(send_text, in_thread=True)
        except axonius_api_client.api.exceptions.UnknownFieldName as exc:
            known_names = "\n\t" + "\n\t".join(exc.known_names)
            send_text = (
                "No such field named {field!r} available in adapter {adapter!r}, "
                "valid field names: {known_names}"
            )
            send_text = send_text.format(
                field=field, adapter=adapter, known_names=known_names
            )
            msg.reply(send_text, in_thread=True)
        except Exception as exc:
            send_text = "Error finding field {field!r} for adapter {adapter!r}: {exc}"
            send_text = send_text.format(field=field, adapter=adapter, exc=exc)
            msg.reply(send_text, in_thread=True)
        return None, None

    def _field_add(self, msg, api_type, adapter, field):
        adapter, field = self._find_field(
            api_type=api_type, adapter=adapter, field=field, msg=msg
        )

        if field and adapter:
            if adapter not in api_type._get_fields:
                api_type._get_fields[adapter] = []
            if field not in api_type._get_fields[adapter]:
                api_type._get_fields[adapter].append(field)
            send_text = "Added field {field!r} for adapter {adapter!r} for {api_type}"
            send_text = send_text.format(
                field=field, adapter=adapter, api_type=api_type._type
            )
            msg.reply(send_text, in_thread=True)

            send_text = self._build_get_fields_lines(api_type=api_type)
            msg.reply(send_text, in_thread=True)

    def _field_del(self, msg, api_type, adapter, field):
        adapter, field = self._find_field(
            api_type=api_type, adapter=adapter, field=field, msg=msg
        )

        if field and adapter:
            if adapter not in api_type._get_fields:
                send_text = "Adapter {adapter} is not in the current {api_type} fields!"
                send_text = send_text.format(
                    adapter=adapter, field=field, api_type=api_type._type
                )
                msg.reply(send_text, in_thread=True)

                send_text = self._build_get_fields_lines(api_type=api_type)
                msg.reply(send_text, in_thread=True)
                return

            if field not in api_type._get_fields[adapter]:
                send_text = (
                    "Field {field} for adapter {adapter} is not in the current "
                    "{api_type} fields!"
                )
                send_text = send_text.format(
                    adapter=adapter, field=field, api_type=api_type._type
                )
                msg.reply(send_text, in_thread=True)

                send_text = self._build_get_fields_lines(api_type=api_type)
                msg.reply(send_text, in_thread=True)
                return

            idx = api_type._get_fields[adapter].index(field)
            api_type._get_fields[adapter].pop(idx)

            if not api_type._get_fields[adapter]:
                del api_type._get_fields[adapter]

            send_text = "Removed field {field!r} for adapter {adapter!r} for {api_type}"
            send_text = send_text.format(
                field=field, adapter=adapter, api_type=api_type._type
            )
            msg.reply(send_text, in_thread=True)

            send_text = self._build_get_fields_lines(api_type=api_type)
            msg.reply(send_text, in_thread=True)

    def _get_saved_queries(self, msg, api_type):
        sqs = api_type.get_saved_query()
        lines = ["Saved Queries for {api_type}:".format(api_type=api_type._type)]

        for sq in sqs:
            line = "\t- *{}*".format(sq["name"])
            lines.append(line)
        send_text = "\n".join(lines)
        msg.reply(send_text, in_thread=True)

    def _get_by_saved_query(self, api_type, msg, value):
        try:
            sq = api_type.get_saved_query_by_name(name=value, regex=False, only1=True)
            rows = list(
                api_type.get(
                    query=sq["view"]["query"]["filter"],
                    manual_fields=sq["view"]["fields"],
                )
            )
        except axonius_api_client.api.exceptions.ObjectNotFound:
            send_text = "No saved query {value} for {api_type} found"
            send_text = send_text.format(api_type=api_type._type, value=value)
            msg.reply(send_text, in_thread=True)
            return
        else:
            TTL_CACHE[msg.thread_ts] = {"api_type": api_type, "rows": rows}
            json_rows = json.dumps(rows, indent=2)
            filename = "{api_type}_{dt}.json".format(api_type=api_type._type, dt=now())
            self._upload_file_reply(msg=msg, filename=filename, content=json_rows)


__all__ = ("cli", "AxonBot", "version")
