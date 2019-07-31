FROM python:3.7-slim

ARG BUILD_DATE
ARG BUILD_VERSION
ARG BUILD_REF

LABEL maintainer="apiclient@axonius.com" \
    org.label-schema.schema-version="1.0" \
    org.label-schema.name="axonius/axonbot_slack" \
    org.label-schema.description="Slack Bot for Axonius" \
    org.label-schema.url="https://axonius.com" \
    org.label-schema.vcs-url="https://github.com/Axonius/axonbot_slack" \
    org.label-schema.vcs-ref=$BUILD_REF \
    org.label-schema.vcs-usage="https://github.com/Axonius/axonbot_slack/blob/master/README.md" \
    org.label-schema.vendor="Axonius" \
    org.label-schema.build-date=$BUILD_DATE \
    org.label-schema.version=$BUILD_VERSION \
    org.label-schema.docker.cmd="docker run --detach --name axonbot_slack --restart always -volume axonbot_slack:/axonbot_slack axonius/axonbot_slack axonbot_slack run" \
    org.label-schema.docker.cmd.help="docker run --rm --name axonbot_slack -volume axonbot_slack:/axonbot_slack axonius/axonbot_slack axonbot_slack --help" \
    org.label-schema.docker.cmd.debug="docker run --rm --name axonbot_slack -volume axonbot_slack:/axonbot_slack axonius/axonbot_slack bash" \
    org.label-schema.docker.cmd.devel="docker run --rm --name axonbot_slack -volume axonbot_slack:/axonbot_slack axonius/axonbot_slack axonbot_slack config" \
    org.label-schema.docker.cmd.test="docker run --rm --name axonbot_slack -volume axonbot_slack:/axonbot_slack axonius/axonbot_slack axonbot_slack test" \
    org.label-schema.docker.params="SLACK_API_TOKEN,AX_URL,AX_KEY,AX_SECRET,HTTPS_PROXY,AX_HTTPS_PROXY,AX_DEVICE_FIELDS,AX_USER_FIELDS,AX_LOGLEVEL,LOGLEVEL,AX_DOTENV"

WORKDIR /axonbot_slack
VOLUME /axonbot_slack

ENV TZ="UTC" AX_DOTENV="/axonbot_slack/.env"

RUN set -ex \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir axonbot_slack==$BUILD_VERSION

CMD ["axonbot_slack", "run"]
