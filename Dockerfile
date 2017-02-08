FROM debian:jessie-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential python2.7 python2.7-dev python-pip supervisor \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p \
        /app/logs /app/run \
        /files/incomplete /files/downloads /files/torrents \
    && touch /app/run/app.db \
    && chown -R www-data /app/run /files

COPY app.py manage.py README.md requirements.txt /app/src/

RUN cd /app/src \
    && pip install -U pip \
    && pip install -r requirements.txt

COPY etc/supervisor /etc/supervisor/
COPY etc/config.py /app/src/

VOLUME ["/files/incomplete", "/files/downloads", "/files/torrents"]

EXPOSE 9001

CMD [ "supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf", "--logfile", "/dev/stdout", "--logfile_maxbytes", "0" ]
