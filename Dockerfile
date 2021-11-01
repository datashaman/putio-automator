FROM python:3.9

ARG VERSION 2.1.1

RUN pip install --no-cache-dir --user putio-automator==${VERSION}

ENTRYPOINT ["/root/.local/bin/putio"]
