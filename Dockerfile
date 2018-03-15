FROM debian:jessie-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        cron \
        python-pip \
        python-pkg-resources \
        rsyslog \
        sendmail \
        smbclient \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p \
        /etc/auto.master.d \
        /files/incomplete /files/downloads /files/torrents \
        /var/www \
        /var/log/putio-automator \
        /var/log/supervisor \
    && chown -R www-data /files /var/www \
    && usermod -u 1000 www-data

COPY etc/config.py.dist /usr/local/share/putio-automator/config.py
COPY etc/cron /etc/cron.d/putio-automator
COPY etc/rsyslog.conf /etc/rsyslog.conf
COPY etc/supervisor.conf /etc/supervisor/conf.d/putio-automator.conf
COPY etc/supervisord.conf /etc/supervisor/supervisord.conf

RUN chmod go= /etc/cron.d/putio-automator

RUN pip install putio-automator \
    && rm -rf $HOME/.cache /tmp/pip_build_root

ENV INITSYSTEM on
ENV PUTIO_ROOT 0

EXPOSE 9001

ENTRYPOINT [ "putio" ]

CMD [ "docker", "bootstrap" ]
