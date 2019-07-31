.. include:: .special.rst

Get commands
#####################################################
All of these commands will reply to you in a thread with the matching objects in JSON format.

See :ref:`Thread Example Responses` for examples of what the thread responses will look like.

See :ref:`Thread sub-commands` for examples of using sub-commands in the thread responses.

Get device commands
====================================================

* :blue:`get device hostname`: Get devices by hostname using an exact search or by regex search with re=value.
* :blue:`get device ip`: Get devices by IP address using an exact search or by regex search with re=value.
* :blue:`get device mac`: Get devices by MAC address using an exact search or by regex search with re=value.
* :blue:`get device query`: Get devices by a query created using the Query Wizard in the Axonius GUI.

  You need to enclose the query using backticks like:

  .. code-block:: console

      @AxonBot get device query ```(specific_data.data.id == ({"$exists":true,"$ne": ""}))```

  .. image:: _static/images/axonbot_get_device_query.png

Get user commands
====================================================

* :blue:`get user username`: Get users by username using an exact search or by regex search with re=value.
* :blue:`get user email`: Get users by email address using an exact search or by regex search with re=value.
* :blue:`get user query`: Get users by a query created using the Query Wizard in the Axonius GUI.

  You need to enclose the query using backticks like:

  .. code-block:: console

      @AxonBot get user query ```(specific_data.data.id == ({"$exists":true,"$ne": ""}))```

  .. image:: _static/images/axonbot_get_user_query.png
