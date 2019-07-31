.. include:: .special.rst

Variables
#####################################################

:ref:`Required Variables` and :ref:`Optional Variables` can be configured using the bot script with the ``config`` action, or you can set them before hand by:

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

.. toctree::

   variables_required.rst
   variables_optional.rst
