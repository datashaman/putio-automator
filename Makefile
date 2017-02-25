TAG = datashaman/putio-automator

HOST_DOWNLOADS = `pwd`/tmp/downloads
HOST_INCOMPLETE = `pwd`/tmp/incomplete
HOST_TORRENTS = `pwd`/tmp/torrents

clean:
	python setup.py clean
	find . -name '*.pyc' -delete
	rm -rf build dist .eggs putio_automator.egg-info sdist

restart-watcher:
	sudo supervisorctl restart watcher

docker-run:
	docker run --rm -i \
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

docker-push:
	docker push $(TAG)

docker-prune-stopped:
	docker ps -a -q | xargs -r docker rm

docker-prune-untagged:
	docker images | grep '^<none>' | awk '{print $$3}' | xargs -r docker rmi

docker-prune: docker-prune-stopped docker-prune-untagged

# npm i -g marked-toc --save
# apt install pandoc
readme-generate:
	toc
	cat -s README.md > /tmp/readme && mv /tmp/readme README.md
	pandoc -f markdown -t rst README.md > README.rst
	sed -i '/.. raw:: html/,+3d' README.rst

prepare-upload: clean
	python setup.py sdist
	python setup.py bdist_wheel

upload: prepare-upload
	twine upload dist/*
