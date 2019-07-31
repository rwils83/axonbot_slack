"""Axonbot plugin package for slack-machine."""
import datetime
import json
import logging
import platform
import sys

import axonius_api_client

from machine.plugins import base
from machine.plugins import decorators
from machine.utils import text
from machine.slack import MessagingClient
from machine.singletons import Slack

import cachetools
import requests

TTL_CACHE = cachetools.TTLCache(maxsize=512, ttl=10 * 60)

LABELS_CMD = "labels "
ADD_CMD = "add "
DELETE_CMD = "delete "

LABELS_SUB_CMDS = [
    {"cmd": ADD_CMD, "action": "Added", "method": "add_labels_by_rows"},
    {"cmd": DELETE_CMD, "action": "Deleted", "method": "delete_labels_by_rows"},
]

FIELDS_DEVICE = "generic:last_seen,labels,hostname,network_interfaces"
FIELDS_DEVICE_EXAMPLE_LIST = [FIELDS_DEVICE, "aws:aws_device_type"]
FIELDS_DEVICE_EXAMPLE = "example device fields: {!r}".format(
    ";".join(FIELDS_DEVICE_EXAMPLE_LIST)
)

FIELDS_USER = "generic:last_seen,labels,username,mail"
FIELDS_USER_EXAMPLE_LIST = [FIELDS_USER, "active_directory:last_bad_logon"]
FIELDS_USER_EXAMPLE = "example user fields: {!r}".format(
    ";".join(FIELDS_USER_EXAMPLE_LIST)
)

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


def splitrip(obj, split):
    """Pass."""
    vals = [x.strip() for x in obj.split(split) if x.strip()]
    return vals


class AxonError(Exception):
    """Pass."""

    def __init__(self, msg, exc):
        """Pass."""
        self.msg = msg
        self.exc = exc
        super(AxonError, self).__init__(msg)


class ParseFields(object):
    """Pass."""

    def parse_str(self, fields_str, example):
        """Pass."""
        self.new_fields = {}
        self.fields_str = fields_str
        self.fields_sets = splitrip(obj=fields_str, split=";")
        self.parse_sets(fields_sets=self.fields_sets, example=example)
        return self.new_fields

    def parse_sets(self, fields_sets, example):
        """Pass."""
        self.new_fields = {}
        for fields_set in fields_sets:
            self.parse_set(fields_set=fields_set, example=example)
        return self.new_fields

    def parse_set(self, fields_set, example):
        """Pass."""
        if not hasattr(self, "new_fields"):
            self.new_fields = {}

        post = "in {fields_set!r}\n{example}"
        post = post.format(fields_set=fields_set, example=example)

        new_set = splitrip(fields_set, ":")

        if len(new_set) != 2:
            msg = "Need 'adapter_name:fields' {post}".format(post)
            raise AxonError(msg)

        name, fields_str = new_set
        fields_list = splitrip(fields_str, ",")

        if not fields_list:
            msg = "Need at least one field {post}".format(post)
            raise AxonError(msg)

        if name not in self.new_fields:
            self.new_fields[name] = []

        for field in fields_list:
            if field not in self.new_fields[name]:
                self.new_fields[name].append(field)

        return self.new_fields


class AxonConnection(object):
    """Pass."""

    def __init__(self, settings):
        """Pass."""
        self.settings = settings
        self.log_level = settings.get("AX_LOGLEVEL", logging.INFO)
        self.url = settings["AX_URL"]
        self.ax_key = settings["AX_KEY"]
        self.ax_secret = settings["AX_SECRET"]
        self.user_fields = settings.get("AX_FIELDS_USER", FIELDS_USER) or FIELDS_USER
        self.device_fields = (
            settings.get("AX_FIELDS_DEVICE", FIELDS_DEVICE) or FIELDS_DEVICE
        )
        self.https_proxy = settings.get("AX_HTTPS_PROXY")

    def start(self):
        """Pass."""
        logging.getLogger("axonius_api_client").setLevel(self.log_level)

        self.http_client = axonius_api_client.http.HttpClient(url=self.url)
        self.http_client.session.proxies = {}
        if self.https_proxy:
            self.http_client.session.proxies["https"] = self.https_proxy

        try:
            self.auth_method = axonius_api_client.auth.AuthKey(
                http_client=self.http_client, key=self.ax_key, secret=self.ax_secret
            )
            self.auth_method.login()
        except requests.exceptions.ConnectTimeout as exc:
            msg = "Unable to connect to Axonius Instance using {client}: {exc}"
            msg = msg.format(client=self.http_client, exc=exc)
            raise AxonError(msg=msg, exc=exc)

        self.users = axonius_api_client.api.Users(auth=self.auth_method)
        self.users._type = "users"
        self.users._fields_example = FIELDS_USER_EXAMPLE
        self.users.response_fields = self.parse_fields(
            api_type=self.users, fields=self.user_fields, example=FIELDS_USER_EXAMPLE
        )

        self.devices = axonius_api_client.api.Devices(auth=self.auth_method)
        self.devices._type = "devices"
        self.devices._fields_example = FIELDS_DEVICE_EXAMPLE
        self.devices.response_fields = self.parse_fields(
            api_type=self.devices,
            fields=self.device_fields,
            example=FIELDS_DEVICE_EXAMPLE,
        )

        self.start_dt = datetime.datetime.utcnow()

    def parse_fields(self, api_type, fields, example):
        """Pass."""
        if isinstance(fields, str):
            parser = ParseFields()
            fields = parser.parse_str(fields_str=fields, example=example)

        new_fields = {}

        for adapter, field_list in fields.items():
            for field in field_list:
                new_adapter, new_field = self.find_field(
                    api_type=api_type, adapter=adapter, field=field
                )
                if new_adapter not in new_fields:
                    new_fields[new_adapter] = []

                if new_field not in new_fields[new_adapter]:
                    new_fields[adapter].append(new_field)
        return new_fields

    def find_field(self, api_type, adapter, field):
        """Pass."""
        try:
            known_fields = api_type.get_fields()
        except Exception as exc:
            msg = "Error fetching {api_type} fields: {exc}"
            msg = msg.format(api_type=api_type._type, exc=exc)
            logger.exception(msg)
            raise AxonError(msg, exc)

        try:
            if adapter != "generic":
                known_adapters = list(known_fields["specific"].keys())
                adapter = axonius_api_client.api.utils.find_adapter(
                    name=adapter, known_names=known_adapters
                )
        except axonius_api_client.api.exceptions.UnknownAdapterName as exc:
            known_names = "\n\t" + "\n\t".join(["generic"] + exc.known_names)
            msg = (
                "No such adapter named {adapter!r}, valid adapter names: {known_names}"
            )
            msg = msg.format(adapter=adapter, known_names=known_names)
            raise AxonError(msg, exc)
        except Exception as exc:
            msg = "Error finding {api_type} adapter named {adapter!r}: {exc}"
            msg = msg.format(api_type=api_type._type, adapter=adapter, exc=exc)
            logger.exception(msg)
            raise AxonError(msg, exc)

        try:
            field = axonius_api_client.api.utils.find_field(
                name=field, adapter=adapter, fields=known_fields
            )
        except axonius_api_client.api.exceptions.UnknownFieldName as exc:
            known_names = "\n\t" + "\n\t".join(exc.known_names)
            msg = (
                "No such field named {field!r} available in adapter {adapter!r}, "
                "valid field names: {known_names}"
            )
            msg = msg.format(field=field, adapter=adapter, known_names=known_names)
            raise AxonError(msg, exc)
        except Exception as exc:
            msg = "Error finding field {field!r} for adapter {adapter!r}: {exc}"
            msg = msg.format(field=field, adapter=adapter, exc=exc)
            logger.exception(msg)
            raise AxonError(msg, exc)

        return adapter, field


@decorators.required_settings(["AX_URL", "AX_KEY", "AX_SECRET"])
class AxonBotSlack(base.MachineBasePlugin):
    """Axonius Slack Bot."""

    def init(self):
        """Pass."""
        self.api = AxonConnection(settings=self.settings)
        self.api.start()
        m = "Axonius connected: {auth_method}!"
        m = m.format(auth_method=self.api.auth_method)
        text.announce(m)

    @property
    def _instance_link(self):
        msg = "<{url}|Axonius Instance at {url!r}>"
        return msg.format(url=self.api.http_client.url)

    @property
    def _bot_link(self):
        return "<https://github.com/Axonius/axonbot_slack|Bot Site>"

    @property
    def _vendor_link(self):
        return "<https://www.axonius.com/|Axonius Site>"

    @property
    def _pyver(self):
        return "Python: *{}*".format(format(sys.version).split()[0])

    @property
    def _platver(self):
        return "Platform: *{}*".format(platform.platform())

    @property
    def _uptime(self):
        uptime = datetime.datetime.utcnow() - self.api.start_dt
        return "Uptime: *{}*".format(format(uptime).split(".")[0])

    @decorators.respond_to(regex=r"^hello$")
    def hello(self, msg):
        """hello: Get a friendly message from skynet"""
        send_text = [
            self._pyver,
            self._platver,
            self._uptime,
            self._instance_link,
            self._bot_link,
            self._vendor_link,
        ]
        send_text = "\n".join(send_text)
        msg.reply(send_text)

    @decorators.respond_to(regex=r"^count device$")
    def count_device(self, msg):
        """count device: Get the count of all devices in the system."""
        count = self.api.devices.get_count()
        send_text = "Total devices: {count}"
        send_text = send_text.format(count=count)
        msg.reply(send_text, in_thread=True)

    @decorators.respond_to(regex=r"^count user$")
    def count_user(self, msg):
        """count user: Get the count of all users in the system."""
        count = self.api.users.get_count()
        send_text = "Total users: {count}"
        send_text = send_text.format(count=count)
        msg.reply(send_text, in_thread=True)

    @decorators.respond_to(regex=r"^fields user$")
    def fields_user(self, msg):
        """fields user: Show the fields that will be returned in responses."""
        send_text = self._build_fields_text(api_type=self.api.users)
        msg.reply(send_text, in_thread=True)

    @decorators.respond_to(regex=r"^fields user add (?P<adapter>\S+) (?P<field>\S+)")
    def fields_user_add(self, msg, adapter, field):
        """fields user add [adapter] [field]: Add an adapters field for user responses."""  # noqa
        self._field_add(msg=msg, api_type=self.api.users, adapter=adapter, field=field)

    @decorators.respond_to(regex=r"^fields user delete (?P<adapter>\S+) (?P<field>\S+)")
    def fields_user_delete(self, msg, adapter, field):
        """fields user delete [adapter] [field]: Delete an adapters field for user responses."""  # noqa
        self._field_del(msg=msg, api_type=self.api.users, adapter=adapter, field=field)

    @decorators.respond_to(regex=r"^fields device$")
    def fields_device(self, msg):
        """fields device: Show the fields that will be returned in responses."""  # noqa
        send_text = self._build_fields_text(api_type=self.api.devices)
        msg.reply(send_text, in_thread=True)

    @decorators.respond_to(regex=r"^fields device add (?P<adapter>\S+) (?P<field>\S+)")
    def fields_device_add(self, msg, adapter, field):
        """fields device add [adapter] [field]: Add an adapters field for device responses."""  # noqa
        self._field_add(
            msg=msg, api_type=self.api.devices, adapter=adapter, field=field
        )

    @decorators.respond_to(
        regex=r"^fields device delete (?P<adapter>\S+) (?P<field>\S+)"
    )
    def fields_device_delete(self, msg, adapter, field):
        """fields device delete [adapter] [field]: Delete an adapters field for device responses."""  # noqa
        self._field_del(
            msg=msg, api_type=self.api.devices, adapter=adapter, field=field
        )

    @decorators.respond_to(regex=r"^get user query ```(?P<value>.*)```")
    def user_by_query(self, msg, value):
        """get user query [value]: Get users by a query generated by Axonius, value must be fenced with triple backticks"""  # noqa
        self._fetch_query(api_type=self.api.users, query=value, msg=msg)

    @decorators.respond_to(regex=r"^get user username (?P<value>\S+)")
    def user_by_username(self, msg, value):
        """get user username [value]: Get users by username (prefix value with *re=* to use regex)"""  # noqa
        self._fetch_by(
            api_type=self.api.users,
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
            api_type=self.api.users,
            value_name="email",
            value=value,
            field="mail",
            field_adapter="generic",
            msg=msg,
        )

    @decorators.respond_to(regex=r"^get device query ```(?P<value>.*)```")
    def device_by_query(self, msg, value):
        """get device query [value]: Get devices by a query generated by Axonius, value must be fenced with triple backticks"""  # noqa
        self._fetch_query(api_type=self.api.devices, query=value, msg=msg)

    @decorators.respond_to(regex=r"^saved query users (?P<value>\S.*)")
    def get_by_saved_query_users(self, msg, value):
        """saved query users [value]: Get all of the users from a saved query"""
        self._get_by_saved_query(msg=msg, api_type=self.api.users, value=value)

    @decorators.respond_to(regex=r"^saved query devices (?P<value>\S.*)")
    def get_by_saved_query_devices(self, msg, value):
        """saved query devices [value]: Get all of the devices from a saved query"""
        self._get_by_saved_query(msg=msg, api_type=self.api.devices, value=value)

    @decorators.respond_to(regex=r"^saved query devices$")
    def get_device_saved_queries(self, msg):
        """saved query devices: Get a list of all saved queries for devices"""
        self._get_saved_queries(msg=msg, api_type=self.api.devices)

    @decorators.respond_to(regex=r"^saved query users$")
    def get_user_aved_queries(self, msg):
        """saved query users: Get a list of all saved queries for users"""
        self._get_saved_queries(msg=msg, api_type=self.api.users)

    @decorators.respond_to(regex=r"^get device hostname (?P<value>\S+)")
    def device_by_hostname(self, msg, value):
        """get device hostname [value]: Get devices by hostname (prefix value with *re=* to use regex)"""  # noqa
        self._fetch_by(
            api_type=self.api.devices,
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
            api_type=self.api.devices,
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
            api_type=self.api.devices,
            value_name="IP Address",
            value=value,
            field="network_interfaces.ips",
            field_adapter="generic",
            msg=msg,
        )

    @decorators.process("message")
    def handle_thread(self, event):
        """thread commands: labels add|remove foo1,foo2,foo3."""
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

        label_list = splitrip(labels, ",")
        if not label_list:
            send_text = "No labels provided, provide a CSV list of labels!"
            msg.reply(send_text, in_thread=True)
            return

        change_method = getattr(cache_entry["api_type"], label_sub_cmd["method"])
        changed = change_method(rows=cache_entry["rows"], labels=label_list)
        send_text = "{action} labels {labels!r} on {changed} {api_type}"
        send_text = send_text.format(
            action=label_sub_cmd["action"],
            labels=", ".join(label_list),
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
                api_type.get(query=query, row_count_min=1, **api_type.response_fields)
            )
        except axonius_api_client.api.exceptions.TooFewObjectsFound:
            send_text = "No {api_type} found using query {query!r}"
            send_text = send_text.format(api_type=api_type._type, query=query)
            msg.reply(send_text, in_thread=True)
        except Exception as exc:
            send_text = "Error fetching {api_type} using query {query!r}: {exc}"
            send_text = send_text.format(api_type=api_type._type, query=query, exc=exc)
            logger.exception(send_text)
            msg.reply(send_text, in_thread=True)
        else:
            TTL_CACHE[msg.thread_ts] = {"api_type": api_type, "rows": rows}
            json_rows = json.dumps(rows, indent=2)
            filename = "{api_type}_{dt}.json".format(api_type=api_type._type, dt=now())
            self._upload_file_reply(msg=msg, filename=filename, content=json_rows)

    def _fetch_by(self, api_type, value_name, value, field, field_adapter, msg):
        kwargs = {}
        kwargs.update(api_type.response_fields)
        kwargs["field"] = field
        kwargs["field_adapter"] = field_adapter
        kwargs["row_count_min"] = 1
        kwargs["row_count_max"] = None

        if value.lower().startswith("re="):
            kwargs["value"] = lstrip(value, "re=").strip()
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
            logger.exception(send_text)
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

    def _build_fields_text(self, api_type):
        lines = ["Current fields for {api_type}:".format(api_type=api_type._type)]

        for k, v in api_type.response_fields.items():
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
            logger.exception(send_text)
            msg.reply(send_text, in_thread=True)
        return None, None

    def _field_add(self, msg, api_type, adapter, field):
        try:
            adapter, field = self.api.find_field(
                api_type=api_type, adapter=adapter, field=field
            )
        except AxonError as exc:
            msg.reply(exc.msg, in_thread=True)
            return

        if adapter not in api_type.response_fields:
            api_type.response_fields[adapter] = []

        if field in api_type.response_fields[adapter]:
            send_text = (
                "Field {field!r} for adapter {adapter!r} for {api_type} already exists"
            )
            send_text = send_text.format(
                field=field, adapter=adapter, api_type=api_type._type
            )
        else:
            api_type.response_fields[adapter].append(field)

            send_text = "Added field {field!r} for adapter {adapter!r} for {api_type}"
            send_text = send_text.format(
                field=field, adapter=adapter, api_type=api_type._type
            )

        msg.reply(send_text, in_thread=True)

        fields_text = self._build_fields_text(api_type=api_type)
        msg.reply(fields_text, in_thread=True)

    def _field_del(self, msg, api_type, adapter, field):
        try:
            adapter, field = self.api.find_field(
                api_type=api_type, adapter=adapter, field=field
            )
        except AxonError as exc:
            msg.reply(exc.msg, in_thread=True)
            return

        if adapter not in api_type._get_fields:
            send_text = "Adapter {adapter!r} is not in the current {api_type} fields!"
            send_text = send_text.format(
                adapter=adapter, field=field, api_type=api_type._type
            )
        elif field in api_type._get_fields[adapter]:
            idx = api_type._get_fields[adapter].index(field)
            api_type._get_fields[adapter].pop(idx)

            if not api_type._get_fields[adapter]:
                del api_type._get_fields[adapter]

            send_text = "Removed field {field!r} for adapter {adapter!r} for {api_type}"
            send_text = send_text.format(
                field=field, adapter=adapter, api_type=api_type._type
            )
        else:
            send_text = (
                "Field {field} for adapter {adapter} is not in the current "
                "{api_type} fields!"
            )
            send_text = send_text.format(
                adapter=adapter, field=field, api_type=api_type._type
            )

        msg.reply(send_text, in_thread=True)

        fields_text = self._build_fields_text(api_type=api_type)
        msg.reply(fields_text, in_thread=True)

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
