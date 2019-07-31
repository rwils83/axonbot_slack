.. include:: .special.rst

Using Docker
#####################################################
* You will need to `install Docker for your platform <https://docs.docker.com/install/>`_
* This is the recommended method of deploying this bot:

  * It will keep the bot self-contained
  * It can handle always re-starting the bot on failure.

* Optional variable passthrus to Docker:

  * Pass variables that are defined in your shell by adding this to your :blue:`docker run` commands:

    .. code-block:: console

        $ docker \
            --env=SLACK_API_TOKEN \
            --env=AX_URL \
            --env=AX_KEY \
            --env=AX_SECRET \
            --env=HTTPS_PROXY \
            --env=AX_HTTPS_PROXY \
            --env=LOGLEVEL \
            --env=AX_LOGLEVEL \
            --env=AX_USER_FIELDS \
            --env=AX_DEVICE_FIELDS

  * Pass variables that are defined manually by adding this to your :blue:`docker run` commands:

    .. code-block:: console

        $ docker \
            --env=SLACK_API_TOKEN="x" \
            --env=AX_URL="x" \
            --env=AX_KEY="x" \
            --env=AX_SECRET="x" \
            --env=HTTPS_PROXY="x" \
            --env=AX_HTTPS_PROXY="x" \
            --env=LOGLEVEL="x" \
            --env=AX_LOGLEVEL="x" \
            --env=AX_USER_FIELDS="x" \
            --env=AX_DEVICE_FIELDS="x"

Download Docker image
=====================================================

.. code-block:: console

    $ docker pull axonius/axonbot_slack:latest

Configure bot in Docker
=====================================================
Use this to be prompted for all of the bots :ref:`Variables`.

* Create a container named :blue:`axonbot_slack` from the image :blue:`axonious/axonbot_slack:latest`.
* Create (or re-use an existing) volume named :blue:`axonbot_slack` and mount it inside the countainer at :blue:`/axoxnbot_slack`.
* Run the container interactively with the command :blue:`axonbot_slack config`.
* Remove the container (but not the volume) named :blue:`axoxnbot_slack` after the command finishes.

.. code-block:: console

    $ docker run \
        --rm \
        --interactive \
        --tty \
        --name="axonbot_slack" \
        --volume="axonbot_slack:/axonbot_slack" \
        axonius/axonbot_slack:latest \
        axonbot_slack config

Test bot in Docker
=====================================================
Use this to make sure the bot is configured correctly and can connect to Slack and Axonius.

* Create a container named :blue:`axonbot_slack` from the image :blue:`axonious/axonbot_slack:latest`.
* Create (or re-use an existing) volume named :blue:`axonbot_slack` and mount it inside the countainer at :blue:`/axoxnbot_slack`.
* Run the container interactively with the command :blue:`axonbot_slack test`.
* Remove the container (but not the volume) named :blue:`axoxnbot_slack` after the command finishes.

.. code-block:: console

    $ docker run \
        --rm \
        --interactive \
        --tty \
        --name="axonbot_slack" \
        --volume="axonbot_slack:/axonbot_slack" \
        axonius/axonbot_slack:latest \
        axonbot_slack test

Run bot in Docker
=====================================================
Use this to run the bot interactively so you can see that the bot starts up properly.

* Create a container named :blue:`axonbot_slack` from the image :blue:`axonious/axonbot_slack:latest`.
* Create (or re-use an existing) volume named :blue:`axonbot_slack` and mount it inside the countainer at :blue:`/axoxnbot_slack`.
* Run the container interactively with the default command :blue:`axonbot_slack run`.
* Remove the container (but not the volume) named :blue:`axoxnbot_slack` after the command finishes.

.. code-block:: console

    $ docker \
        run \
        --rm \
        --interactive \
        --tty \
        --name="axonbot_slack" \
        --volume="axonbot_slack:/axonbot_slack" \
        axonius/axonbot_slack:latest

Run bot in production mode in Docker
=====================================================
Use this to run the bot detached and to always restart on failure.

* Create a container named :blue:`axonbot_slack` from the image :blue:`axonious/axonbot_slack:latest`.
* Create (or re-use an existing) volume named :blue:`axonbot_slack` and mount it inside the countainer at :blue:`/axoxnbot_slack`.
* Run the container detached with the default command :blue:`axonbot_slack run`.
* This will *NOT* remove the container if it is stopped.

.. code-block:: console

    $ docker \
        run \
        --detach \
        --restart always \
        --name="axonbot_slack" \
        --volume="axonbot_slack:/axonbot_slack" \
        axonius/axonbot_slack:latest

To stop a detached docker for this bot.

.. code-block:: console

    $ docker stop axonbot_slack

To start a previously stopped detached docker for this bot.

.. code-block:: console

    $ docker start axonbot_slack
