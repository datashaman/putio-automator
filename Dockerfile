FROM debian:jessie-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        cron \
        git-core \
        python2.7 \
        python2.7-dev \
        python-pip \
        supervisor \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p \
        /app/logs /app/run \
        /files/incomplete /files/downloads /files/torrents \
        /var/www \
    && touch /app/run/app.db /var/log/cron.log \
    && chown -R www-data /app/logs /app/run /files /var/www

COPY . /app/src/

RUN cd /app/src \
    && pip install 'pbr>=1.9' \
    && pip install 'setuptools>=17.1' \
    && pip install -U pip \
    && pip install .

COPY etc/supervisor /etc/supervisor/
COPY etc/config.py.dist /app/src/config.py
COPY etc/cron /etc/cron.d/putio-automator

RUN usermod -u 1000 www-data

EXPOSE 9001
ENTRYPOINT [ "putio" ]
CMD [ "docker", "bootstrap" ]
