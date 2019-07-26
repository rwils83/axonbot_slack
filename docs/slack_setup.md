<!-- MarkdownTOC -->

- [AxonBot Slack Setup](#axonbot-slack-setup)
    - [Create a Slack application](#create-a-slack-application)
        - [Create the App](#create-the-app)
    - [Add features](#add-features)
        - [Add a bot user](#add-a-bot-user)
    - [Install the App](#install-the-app)
    - [Configure display information](#configure-display-information)
    - [Get the Slack API token](#get-the-slack-api-token)

<!-- /MarkdownTOC -->

# AxonBot Slack Setup

AxonBot requires a Slack API Bot token. Here are the steps to generate one for your workspace.

## Create a Slack application

Go to https://api.slack.com/apps and click "Create an App".

![Slack API apps page](images/slack_apps.png)

### Create the App

Fill in the App Name field with something (i.e. AxonBot) and choose the Slack Workspace you want the bot to have access to and click "Create App".

![Slack API apps create form](images/slack_apps_create.png)

## Add features

You will be taken to a "Basic Information" page for the new Slack Bot. Click on the "Bots" box under "Add features and funtionality".

![Slack API apps basic information Step 1](images/slack_app_basic1.png)

### Add a bot user

Click "Add a Bot User".

![Add a Bot User Step 1](images/slack_add_bot_user1.png)

Change the values as you see fit, or accept the defaults and click "Add Bot User".

![Add a Bot User Step 2](images/slack_add_bot_user2.png)

## Install the App

Click "Basic Information" on the left hand side, then under "Install your app to your workspace" click the "Install App to Workspace" button.

![Slack API apps basic information Step 2](images/slack_app_basic2.png)

Click the "Confirm button" to authorize the bot user to access your workspace.

![Install Confirm](images/slack_install_confirm.png)

## Configure display information

Optionally, click "Basic Information" on the left hand side and scroll down to "Display Information". Fill in the "Short Description" field. Click the "+ Add App Icon" button and supply [this icon](axlogo512.png). Change the background color as you like, then click the "Save Changes" button on the bottom.

![Display information](images/slack_display_info.png)

## Get the Slack API token

Finally, click "OAuth & Permissions" on the left hand side, and copy the string that starts with "xoxb-" from the "Bot User OAuth Access Token" field. This is the token that you will need to provide to the axonbot as SLACK_API_TOKEN.

![Tokens](images/slack_tokens.png)
