.. include:: .special.rst

Instal using pipenv
#####################################################
* Using `pipenv <https://github.com/pypa/pipenv>`_ allows you to install this into a virtual environment.

Install package using pipenv
=====================================================

.. code-block:: console

    $ pip install --upgrade pipenv
    $ mkdir axonbot_slack
    $ cd axonbot_slack
    $ pipenv install axonbot-slack

    $ # verify the package is installed correctly by running the bot script with no options
    $ pipenv run axonbot_slack

.. raw:: html

   <script id="asciicast-fQsBhtV2dTG5Uhph1odHRCjqB" src="https://asciinema.org/a/fQsBhtV2dTG5Uhph1odHRCjqB.js" async></script>

Configure bot in Pipenv
=====================================================
Use this to be prompted for all of the bots :ref:`Variables`.

.. code-block:: console

    $ pipenv run axonbot_slack config

.. raw:: html

   <script id="asciicast-sBQ6nw98AU6XWtcec3N1bnFGc" src="https://asciinema.org/a/sBQ6nw98AU6XWtcec3N1bnFGc.js" async></script>

Test bot in Pipenv
=====================================================
Use this to make sure the bot is configured correctly and can connect to Slack and Axonius.

.. code-block:: console

    $ pipenv run axonbot_slack test

.. raw:: html

   <script id="asciicast-VRMOdPIRFKAHatZdgx2cBvWeZ" src="https://asciinema.org/a/VRMOdPIRFKAHatZdgx2cBvWeZ.js" async></script>

Run bot in Pipenv
=====================================================
Use this to run the bot.

.. code-block:: console

    $ pipenv run axonbot_slack run
    $ # send commands to the bot in Slack
    $ # Use CTRL + C to stop the bot

.. raw:: html

   <script id="asciicast-h9aVxihMwPVFxZpX1KYoqd547" src="https://asciinema.org/a/h9aVxihMwPVFxZpX1KYoqd547.js" async></script>
