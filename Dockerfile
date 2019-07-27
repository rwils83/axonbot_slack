FROM python:3.7-slim

MAINTAINER Axonius "apiclient@axonius.com"

WORKDIR /home/axonbot
ENV TZ UTC

COPY docker.env /home/axonbot/.env

RUN set -ex && pip install --no-cache-dir --upgrade pip axonbot

CMD ["axonbot", "run"]
