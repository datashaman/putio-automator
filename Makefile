clean:
	find . -name '*.pyc' -delete

restart-watcher:
    sudo supervisorctl restart watcher
