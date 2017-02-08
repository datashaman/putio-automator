TAG = datashaman/putio-automator

HOST_DOWNLOADS = `pwd`/tmp/downloads
HOST_INCOMPLETE = `pwd`/tmp/incomplete
HOST_TORRENTS = `pwd`/tmp/torrents

clean:
	find . -name '*.pyc' -delete

restart-watcher:
	sudo supervisorctl restart watcher

docker-build:
	docker build -t $(TAG) .

docker-run:
	docker run --rm -it \
		-e PUTIO_TOKEN=$(PUTIO_TOKEN)  \
		-p 9001:9001 \
		-v $(HOST_INCOMPLETE):/files/incomplete \
		-v $(HOST_DOWNLOADS):/files/downloads \
		-v $(HOST_TORRENTS):/files/torrents \
		$(TAG)

docker-bash:
	docker run --rm -it \
		-e PUTIO_TOKEN=$(PUTIO_TOKEN)  \
		-p 9001:9001 \
		-v $(HOST_INCOMPLETE):/files/incomplete \
		-v $(HOST_DOWNLOADS):/files/downloads \
		-v $(HOST_TORRENTS):/files/torrents \
		$(TAG) /bin/bash
