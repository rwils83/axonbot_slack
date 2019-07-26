# AxonBot Slack Setup

AxonBot requires a Slack API Bot token. Here are the steps to generate one for your workspace.

## Create a Slack application

Go to https://api.slack.com/apps and click "Create an App".

![Slack API apps page](api_slack_apps.png)

Fill in the App Name field with something (i.e. AxonBot) and choose the Slack Workspace you want the bot to have access to and click "Create App".

![Slack API apps create form](api_slack_apps_create.png)

You will be taken to a "Basic Information" page for the new Slack Bot. Click on the "Bots" box under "Add features and funtionality".

![Slack API apps basic information Step 1](api_slack_app_basic1.png)

Click "Add a Bot User".

![Add a Bot User Step 1](add_bot_user1.png)

Change the values as you see fit, or accept the defaults and click "Add Bot User".

![Add a Bot User Step 2](add_bot_user2.png)

Click "Basic Information" on the left hand side, then under "Install your app to your workspace" click the "Install App to Workspace" button.

![Slack API apps basic information Step 2](api_slack_app_basic2.png)

Click the "Confirm button" to authorize the bot user to access your workspace.

![Install Confirm](install_confirm.png)

Optionally, click "Basic Information" on the left hand side and scroll down to "Display Information". Fill in the "Short Description" field. Click the "+ Add App Icon" button and supply [this icon](axlogo512.png). Change the background color as you like, then click the "Save Changes" button on the bottom.

![Display information](display_info.png)

Finally, click "OAuth & Permissions" on the left hand side, and copy the string that starts with "xoxb-" from the "Bot User OAuth Access Token" field. This is the token that you will need to provide to the axonbot as SLACK_API_TOKEN.

![Tokens](tokens.png)
