FROM docker.io/library/python:3.13.0

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8

# install gosu
RUN apt-get update \
    && \
    apt-get install -y --no-install-recommends \
      gosu=1.14-1+b10 \
    && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY . /usr/src/app/

RUN pip3 --no-cache-dir install .

# set entrypoint
ENTRYPOINT ["./custom-entrypoint"]

# set command
CMD ["/usr/local/bin/harvestr"]
