FROM python:3.7-slim

ARG BUILD_DATE
ARG BUILD_VERSION
ARG BUILD_REF

LABEL maintainer="apiclient@axonius.com" \
    org.label-schema.schema-version="1.0" \
    org.label-schema.name="axonius/axonbot" \
    org.label-schema.description="Slack Bot for Axonius" \
    org.label-schema.url="https://axonius.com" \
    org.label-schema.vcs-url="https://github.com/Axonius/axonbot" \
    org.label-schema.vcs-ref=$BUILD_REF \
    org.label-schema.vcs-usage="https://github.com/Axonius/axonbot/blob/master/README.md" \
    org.label-schema.vendor="Axonius" \
    org.label-schema.build-date=$BUILD_DATE \
    org.label-schema.version=$BUILD_VERSION \
    org.label-schema.docker.cmd="docker run --detach --name axonbot --restart always -volume axonbot:/axonbot axonius/axonbot axonbot run" \
    org.label-schema.docker.cmd.help="docker run --rm --name axonbot -volume axonbot:/axonbot axonius/axonbot axonbot --help" \
    org.label-schema.docker.cmd.debug="docker run --rm --name axonbot -volume axonbot:/axonbot axonius/axonbot bash" \
    org.label-schema.docker.cmd.devel="docker run --rm --name axonbot -volume axonbot:/axonbot axonius/axonbot axonbot config" \
    org.label-schema.docker.cmd.test="docker run --rm --name axonbot -volume axonbot:/axonbot axonius/axonbot axonbot test" \
    org.label-schema.docker.params="SLACK_API_TOKEN,AX_URL,AX_KEY,AX_SECRET,HTTPS_PROXY,AX_HTTPS_PROXY,AX_DEVICE_FIELDS,AX_USER_FIELDS,AX_LOGLEVEL,LOGLEVEL"

WORKDIR /axonbot
VOLUME /axonbot

ENV TZ="UTC" AX_DOTENV="/axonbot/.env"

RUN set -ex \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir axonbot

CMD ["axonbot", "run"]
