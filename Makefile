pip_location = /opt/wot/venv/bin/pip3

systemd_units = wot-binding.service wot-thing-directory.service wot-proxy.service wot-adapter.service
systemd_units_dest = $(addprefix /lib/systemd/system/, $(systemd_units))

config_services = thing_directory proxy binding
config_files_dest = $(addprefix /etc/opt/wot/, $(addsuffix .cfg, $(config_services)))

yaml_config = adapter.yaml
yaml_config_dest = $(addprefix /opt/wot/config/, $(yaml_config))

install-deps:
	apt-get update
	apt-get install -y python3 python3-venv python3-dev build-essential autoconf

install: install-python install-user install-files

install-python: $(pip_location)
	$< install wheel gunicorn Cython
	$< install .

install-files: install-services install-config

$(pip_location):
	mkdir -p /opt/wot
	python3 -m venv /opt/wot/venv

install-user:
	install -dm 0755 /var/opt/wot/
	getent group wot >/dev/null 2>&1 || groupadd wot
	getent passwd wot >/dev/null 2>&1 || useradd -d /var/opt/wot/lib/ -m -g wot wot

install-services: $(systemd_units_dest)
	systemctl daemon-reload 2>/dev/null || true

$(systemd_units_dest): /lib/systemd/system/%.service: lib/systemd/system/%.service
	install -m 0644 $< $@

install-config: $(config_files_dest) $(yaml_config_dest)

/etc/opt/wot/:
	install -dm 0755 $@

$(config_files_dest): | /etc/opt/wot/
$(config_files_dest): /etc/opt/wot/%.cfg: wot/%/config.py
	install -m 0644 $< $@

/opt/wot/config/:
	install -dm 0755 $@

$(yaml_config_dest): | /opt/wot/config/
$(yaml_config_dest): /opt/wot/config/%: config/%
	install -m 0644 $< $@

uninstall:
	systemctl stop $(systemd_units)
	systemctl disable $(systemd_units)
	rm -rf $(systemd_units_dest)
	rm -rf /var/opt/wot/
	rm -rf /opt/wot/
	systemctl daemon-reload 2>/dev/null || true
	userdel -rf wot
	groupdel wot

.PHONY = install-deps install uninstall install-files install-services install-config
