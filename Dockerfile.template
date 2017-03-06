FROM resin/%%RESIN_MACHINE_NAME%%-python:slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        cifs-utils \
        cron \
        python-pip \
        python-setuptools \
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

COPY etc/rsyslog.conf /etc/rsyslog.conf
COPY etc/supervisor.conf-rpi /etc/supervisor/conf.d/putio-automator.conf
COPY etc/supervisord.conf /etc/supervisor/supervisord.conf
COPY etc/config.py.dist-rpi /usr/local/share/putio-automator/config.py
COPY etc/cron /etc/cron.d/putio-automator
COPY etc/fstab /etc/fstab

RUN chmod go= /etc/cron.d/putio-automator

RUN pip install -U pip setuptools \
    && pip install putio-automator \
    && rm -rf $HOME/.cache /tmp/pip_build_root

ENV INITSYSTEM on

ENTRYPOINT [ "putio" ]

CMD [ "docker", "bootstrap" ]
