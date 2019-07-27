<!-- MarkdownTOC -->

- [AxonBot Slack Setup](#axonbot-slack-setup)
    - [Create a Slack Bot](#create-a-slack-bot)
    - [Get the Slack API token](#get-the-slack-api-token)
    - [Save Integration](#save-integration)
    - [Optional Configurations](#optional-configurations)
        - [Customize Name](#customize-name)
        - [Customize Icon](#customize-icon)
        - [Full Name](#full-name)
        - [What this bot does](#what-this-bot-does)
        - [Restrict API Token Usage](#restrict-api-token-usage)

<!-- /MarkdownTOC -->

# AxonBot Slack Setup

AxonBot requires a Slack API Bot token. Here are the steps to generate one for your workspace.

## Create a Slack Bot

Go to https://my.slack.com/services/new/bot and fill in the Username field (i.e. axonbot), then click "Add bot integration".

![Slack create bot page](images/slack_create_bot_page.png)

## Get the Slack API token

The next page will have an API Token field that starts with ```xoxb-```. This is the token that you will need to provide to axonbot as SLACK_API_TOKEN.

![Token](images/slack_token.png)

## Save Integration

You can fill out the [Optional Configurations](#optional-configurations) below, or you can skip all of that and scroll to the bottom of the page and click the "Save Integration" button.

![Save Integration](images/slack_save.png)

## Optional Configurations

### Customize Name

You can change the name of the bot in slack here.

![Customize Name](images/slack_customize_name.png)

### Customize Icon

Click the "Upload an image" button and supply [this icon](axlogo512.png).

![Customize Icon](images/slack_customize_icon.png)

### Full Name

You can change the display name of the bot in slack here.

![Full Name](images/slack_fullname.png)

### What this bot does

This is a good place to put the Axonius instance this bot works with.

![What this bot does](images/slack_what_this_bot_does.png)

### Restrict API Token Usage

You can fill this in so that the API Token for this bot user can only connect from a specific IP Address range.

![Restrict API Token](images/slack_restrict_api_token.png)

