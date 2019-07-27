FROM python:3.7-alpine

MAINTAINER Axonius "apiclient@axonius.com"

WORKDIR /home/axonbot
ENV TZ UTC

# remove me!
# COPY requirements.txt /home/axonbot/requirements.txt
# remove me!
# ENV PYTHONPATH=/home/axonbot

COPY docker.env /home/axonbot/.env

RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
        python3 \
        python3-dev \
        openssl-dev \
        libffi-dev \
        musl-dev \
        gcc \
    && pip install --no-cache-dir --upgrade pip axonbot \
    && apk del .build-deps \
    && rm -rf /usr/src/python
    # && pip install --no-cache-dir --upgrade -r \
    #     /home/axonbot/requirements.txt \

# remove this!
# COPY axonbot /home/axonbot/axonbot

# change this to just axonbot
# CMD ["python", "/home/axonbot/axonbot/shell.py"]
CMD ["axonbot"]
