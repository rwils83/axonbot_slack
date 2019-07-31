.. include:: .special.rst

Optional Variables
#####################################################

AX_DOTENV
=====================================================
Have the bot use a specific :blue:`.env` file. You can also supply this using the ``--env`` argument to the bot.

Default value: :blue:`"/current_working_directory/.env"`

.. code-block:: console

   $ export AX_DOTENV="/path/to/custom.env"
   # or...
   $ axonbot_slack --env "/path/to/custom.env"

Proxies
=====================================================
Proxies can be supplied in a few different ways (courtesy of `requests proxy support <https://github.com/psf/requests>`_):

* Simple Proxy: :blue:`"https://10.10.1.10:3128"`
* Basic Auth Proxy: :blue:`"https://user:pass@10.10.1.10:3128"`
* Socks Proxy: :blue:`"socks5://user:pass@10.10.1.10:3128"`

HTTPS_PROXY
-----------------------------------------------------
Proxy to use for the :ref:`Connection to the Slack API`.

Default value: :blue:`""`

AX_HTTPS_PROXY
-----------------------------------------------------
Proxy to use for the :ref:`Connection to the Axonius instance`.

Default value: :blue:`""`

Object Fields
======================================================
You can always add or remove fields by sending commands to the bot, but this allows you to change the default set of fields that the bot starts with for user and device objects.

These variables need to have an :green:`adapter` followed by a colon then followed by a comma seperated list of fields.

* Fields can be considered the "columns" to return in response objects.
* The :blue:`generic` adapter relates to the correlated fields as displayed in the :blue:`General Data` tab of an object in the Axonius GUI.
* Fields from multiple adapters can be defined by seperating them with a semi-colon.

The :green:`adapter` must be either :blue:`generic` or the name of a valid adapter in the Axonius instance.

* If an invalid adapter name is supplied, the bot will print a list of valid adapter names and exit.

Each field in the comma seperated list of fields must be a valid field for the adapter.

* If an invalid field name is supplied, the bot will print a list of valid fields for the adapter and exit.

Example for specifying a set of fields for just the generic adapter:

.. code-block:: json

   "generic:labels,hostname,network_interfaces,last_seen"

Example for specifying a set of fields for just one non-generic adapter :

.. code-block:: json

   "aws:aws_device_type,aws_source"

Example for specifying a set of fields for the generic adapter and for one non-generic adapter:

.. code-block:: json

   "generic:labels,hostname,network_interfaces,last_seen;aws:aws_device_type,aws_source"

AX_DEVICE_FIELDS
------------------------------------------------------
Default fields to return in device responses.

Default value: :blue:`"generic:labels,hostname,network_interfaces,last_seen"`

AX_USER_FIELDS
------------------------------------------------------
Default fields to return in user responses

Default value: :blue:`"generic:labels,username,last_seen,mail"`

Logging Levels
=====================================================
These levels control the logging output to the console. These are the valid logging levels:

* debug
* info
* warning
* error
* fatal

LOGLEVEL
------------------------------------------------------
Logging level to use for the entire python logging system.

Default value: :blue:`"info"`

AX_LOGLEVEL
------------------------------------------------------
Logging level to use for the Axonius API client. If this value is a lower level than :ref:`LOGLEVEL`, the value from :ref:`LOGLEVEL` will wind up being the actual logging level.

Default value: :blue:`"info"`
