FROM docker.io/library/python:3.10.2

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    XDG_CONFIG_HOME=/config

WORKDIR /usr/src/app
ADD . /usr/src/app

RUN pip3 install .

ENTRYPOINT ["/usr/local/bin/harvestr"]

ARG VCS_REF
ARG VERSION
ARG BUILD_DATE
LABEL maintainer="Andrew Cole <andrew.cole@illallangi.com>" \
      org.label-schema.build-date=${BUILD_DATE} \
      org.label-schema.description="TODO: SET DESCRIPTION" \
      org.label-schema.name="Harvestr" \
      org.label-schema.schema-version="1.0" \
      org.label-schema.url="http://github.com/illallangi/harvestr" \
      org.label-schema.usage="https://github.com/illallangi/harvestr/blob/master/README.md" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/illallangi/harvestr" \
      org.label-schema.vendor="Illallangi Enterprises" \
      org.label-schema.version=$VERSION
