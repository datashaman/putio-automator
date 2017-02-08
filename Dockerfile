FROM debian:jessie-slim

ENV REPO https://github.com/datashaman/putio-automator
ENV COMMIT develop

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git-core python2.7 python2.7-dev python-pip supervisor \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --branch $COMMIT $REPO /app/src \
    && cd /app/src \
    && pip install -U pip \
    && pip install -r requirements.txt

RUN mkdir -p \
        /app/logs /app/run \
        /files/incomplete /files/downloads /files/torrents \
    && chown -R www-data /files

RUN touch /app/run/app.db && chown www-data /app/run /app/run/app.db

COPY etc/supervisor /etc/supervisor
COPY etc/config.py /app/src/config.py

VOLUME ["/files/incomplete", "/files/downloads", "/files/torrents"]

EXPOSE 9001

CMD [ "supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf", "--logfile", "/dev/stdout", "--logfile_maxbytes", "0" ]
