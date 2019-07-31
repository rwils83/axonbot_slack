.. include:: .special.rst

Using pipenv
#####################################################
* Using `pipenv <https://github.com/pypa/pipenv>`_ allows you to install this into a virtual environment.

Install package using pipenv
=====================================================
* Install pipenv
* Use :blue:`pipenv install axonbot-shell` to create a virtual environment and install the package into it.
* Use :blue:`pipenv run axonbot_shell` to verify the package is installed properly and the bot script is found in the virtual environments PATH.

.. raw:: html

   <script id="asciicast-fQsBhtV2dTG5Uhph1odHRCjqB" src="https://asciinema.org/a/fQsBhtV2dTG5Uhph1odHRCjqB.js" async></script>

Configure bot in Pipenv
=====================================================
* Use :blue:`pipenv run axonbot_shell config` to create a :blue:`.env` file and populate it with prompted values.

.. raw:: html

   <script id="asciicast-sBQ6nw98AU6XWtcec3N1bnFGc" src="https://asciinema.org/a/sBQ6nw98AU6XWtcec3N1bnFGc.js" async></script>

Test bot in Pipenv
=====================================================
* Use :blue:`pipenv run axonbot_shell test` in order to validate the configuration values and the connection to Slack and Axonius.

.. raw:: html

   <script id="asciicast-VRMOdPIRFKAHatZdgx2cBvWeZ" src="https://asciinema.org/a/VRMOdPIRFKAHatZdgx2cBvWeZ.js" async></script>

Run bot in Pipenv
=====================================================
* Use :blue:`pipenv run axonbot_shell run` in order to start the bot.
* Send commands to the bot in Slack.
* Use ``CTRL + C`` to stop the bot.

.. raw:: html

   <script id="asciicast-h9aVxihMwPVFxZpX1KYoqd547" src="https://asciinema.org/a/h9aVxihMwPVFxZpX1KYoqd547.js" async></script>
