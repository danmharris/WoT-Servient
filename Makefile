pip_location = /opt/wot/bin/pip3

install-deps:
	apt-get update
	apt-get install -y python3 python3-venv python3-dev build-essential autoconf

install: install-python install-files

install-python: $(pip_location)
	$< install wheel gunicorn Cython
	$< install .

install-files: /var/opt/wot/lib/ $(config_dest_files)

$(pip_location):
	python3 -m venv /opt/wot/

/var/opt/wot/lib/:
	install -dm 0755 /var/opt/wot/
	getend group wot >/dev/null 2>&1 || groupadd wot
	getent passwd wot >/dev/null 2>&1 || useradd -d /var/opt/wot/lib/ -m -g wot wot

uninstall:
	rm -rf /var/opt/wot/
	rm -rf /opt/wot/
	userdel -rf wot
	groupdel wot

.PHONY = install-deps install uninstall
