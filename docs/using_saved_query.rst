.. include:: .special.rst

Saved Query commands
#####################################################
Commands to get objects in a thread response using saved queries.

See :ref:`Thread Example Responses` for examples of what the thread responses will look like.

See :ref:`Thread sub-commands` for examples of using sub-commands in the thread responses.

Saved Query Device Commands
====================================================

* :blue:`saved query devices`: This will respond to you in a thread with a list of all valid Saved Queries for devices.

  .. image:: _static/images/axonbot_get_user_query.png

  ![saved query devices](images/axonbot_saved_query_devices.png)

Saved Query User Commands
====================================================

* :blue:`saved query users`: This will respond to you in a thread with a list of all valid Saved Queries for users.

  ![saved query devices](images/axonbot_saved_query_devices.png)


## saved query users

This will respond to you in a thread with a list of all Saved Queries for users.

![saved query users](images/axonbot_saved_query_users.png)

## saved query devices query_name

This will all reply to you in a thread with a JSON snippet of all devices returned for the query given as query_name. See [get command response examples](#get-command-response-examples) for examples of what the thread responses will look like, and see [Thread sub-commands](#thread-sub-commands) for examples of using sub-commands in the thread responses.

![saved query devices query_name](images/axonbot_saved_query_devices_query.png)

## saved query users query_name

This works exactly like [saved query devices query_name](#saved-query-devices-query_name).

![saved query users query_name](images/axonbot_saved_query_users_query.png)
