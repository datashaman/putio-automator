FROM debian:jessie-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git-core python2.7 python2.7-dev python-pip supervisor \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p \
        /app/logs /app/run \
        /files/incomplete /files/downloads /files/torrents \
    && touch /app/run/app.db \
    && chown -R www-data /app/logs /app/run /files

COPY . /app/src/

RUN cd /app/src \
    && pip install 'pbr>=1.9' \
    && pip install 'setuptools>=17.1' \
    && pip install -U pip \
    && pip install .

COPY etc/supervisor /etc/supervisor/
COPY etc/config.py /app/src/

RUN usermod -u 1000 www-data

EXPOSE 9001
ENTRYPOINT [ "putio" ]
CMD [ "supervisord" ]
