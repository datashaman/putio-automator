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

docker-prune-stopped:
	docker ps -a -q | xargs -r docker rm

docker-prune-untagged:
	docker images | grep '^<none>' | awk '{print $$3}' | xargs -r docker rmi

docker-prune: docker-prune-stopped docker-prune-untagged

# npm i -g marked-toc --save
# apt install pandoc
readme-generate:
	toc
	pandoc -f markdown -t rst README.md > README.rst

sdist: readme-generate
	python setup.py sdist

bdist_wheel: readme-generate
	python setup.py bdist_wheel

upload: clean sdist bdist_wheel
	twine upload dist/*
