TAG = datashaman/putio-automator

HOST_DOWNLOADS = `pwd`/tmp/downloads
HOST_INCOMPLETE = `pwd`/tmp/incomplete
HOST_TORRENTS = `pwd`/tmp/torrents

clean:
	python setup.py clean
	find . -name '*.pyc' -delete
	rm -rf build dist .eggs putio_automator.egg-info sdist tmp/*/*

readme-generate:
	# toc
	cat -s README.md > /tmp/readme && mv /tmp/readme README.md
	pandoc -f markdown -t rst README.md > README.rst
	sed -i '/.. raw:: html/,+3d' README.rst

prepare-upload: clean
	python setup.py sdist
	python setup.py bdist_wheel

upload: prepare-upload
	twine upload dist/*
