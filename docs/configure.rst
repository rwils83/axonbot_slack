.. include:: .special.rst

Configuring
#####################################################

:ref:`Required Variables` and :ref:`Optional Variables` can be set using the bot config prompts, or you can set them before hand by:

#. Setting the variables in a :blue:`.env` file in your current working directory, and these will be used every time you start the bot:

   .. code-block:: console

     $ touch .env
     $ echo 'AX_URL="https://axonius.instance"' >> .env
     $ echo 'AX_KEY="axonius_user_api_key"' >> .env
     $ echo 'AX_SECRET="axonius_user_api_secret"' >> .env
     $ echo 'SLACK_API_TOKEN="slack_bot_api_token"' >> .env

#. Setting the variables yourself, but these will only last for the current terminal session:

   .. code-block:: console

      $ export AX_URL="https://axonius.instance"
      $ export AX_KEY="axonius_user_api_key"
      $ export AX_SECRET="axonius_user_api_secret"
      $ export SLACK_API_TOKEN="slack_bot_api_token"

Configure using docker
=====================================================
First you want to :ref:`Install using docker`.

.. todo::
   fill this out

Configure using pipenv
=====================================================
First you want to :ref:`Install using pipenv`.

Since this package is not installed in the system wide packages, you'll need to activate the virtual environment first in order for python to find the :blue:`axonbot_slack` package and all of its dependencies.

.. code-block:: console

   $ pipenv shell

You can use the command line tool to prompt you for variables and save them to a :blue:`.env` file in your current working directory:



Configure using pip
=====================================================
First you want to :ref:`Install using pip`.

Configure using github
=====================================================
First you want to :ref:`Install using github`.

