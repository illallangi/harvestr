FROM docker.io/library/python:3.10.7

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8

# install gosu
RUN apt-get update \
    && \
    apt-get install -y --no-install-recommends \
      gosu=1.12-1+b6 \
    && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY . /usr/src/app/

RUN pip3 --no-cache-dir install .

# set entrypoint
ENTRYPOINT ["./custom-entrypoint"]

# set command
CMD ["/usr/local/bin/harvestr"]
