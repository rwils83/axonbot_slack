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

Pull Docker image
=====================================================

.. code-block:: console

    $ docker pull axonius/axonbot_slack:latest

Configure bot in Docker
=====================================================

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

.. code-block:: console

    $ docker run \
        --rm \
        --interactive \
        --tty \
        --name="axonbot_slack" \
        --volume=""axonbot_slack:/axonbot_slack"" \
        axonius/axonbot_slack:latest \
        axonbot_slack test

Run bot in Docker
=====================================================

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

.. code-block:: console

    $ docker \
        run \
        --detach \
        --restart always \
        --name="axonbot_slack" \
        --volume="axonbot_slack:/axonbot_slack" \
        axonius/axonbot_slack:latest

Stop bot in Docker
=====================================================

.. code-block:: console

    $ docker stop axonbot_slack
