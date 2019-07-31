.. include:: .special.rst

Steps to generate an API token for a Slack bot
#####################################################

Create a new Slack bot
=====================================================
Go to https://my.slack.com/services/new/bot and fill in the :blue:`Username` field (i.e. axonbot), then click :blue:`Add bot integration`.

.. image:: _static/images/slack_create_bot_page.png

Get the API token for the New Slack Bot
=====================================================
The :blue:`API Token` field that starts with :blue:`xoxb-` is what you need to provide as :ref:`SLACK_API_TOKEN`.

.. image:: _static/images/slack_token.png

Save Integration
=====================================================
You can do the optional items below.

Or you can skip all of that and scroll to the bottom of the page and click the :blue:`Save Integration` button.

.. image:: _static/images/slack_save.png

Optional Items
=====================================================
You can change the name of the bot here.

.. image:: _static/images/slack_customize_name.png

Customize Icon
-----------------------------------------------------
Click the :blue:`Upload an image` button and supply `this icon <_static/images/axlogo512.png>`_.

.. image:: _static/images/slack_customize_icon.png

Full Name
-----------------------------------------------------
You can change the display name of the bot here.

.. image:: _static/images/slack_fullname.png

What this bot does
-----------------------------------------------------
This is a good place to put the Axonius instance this bot works with.

.. image:: _static/images/slack_what_this_bot_does.png

Restrict API Token Usage
-----------------------------------------------------
You can fill this in so that the API Token for this bot user can only connect from a specific IP Address range.

.. image:: _static/images/slack_restrict_api_token.png
