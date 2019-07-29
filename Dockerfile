FROM python:3.7-slim

MAINTAINER Axonius "apiclient@axonius.com"

WORKDIR /home/axonbot

ENV TZ UTC
ENV AX_DOTENV /home/axonbot/axonbot_config/.env

RUN set -ex \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir axonbot

CMD ["axonbot", "run"]
