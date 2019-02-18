#!/usr/bin/env bash
apt update && apt install python3-venv
python3 -m venv /opt/wot-network
source /opt/wot-network/bin/activate
pip install -r $(dirname $0)/requirements.txt
python3 $(dirname $0)/setup.py install
cp -r $(dirname $0)/etc/systemd/system/* /etc/systemd/system/
cp $(dirname $0)/etc/wot-network.ini /etc/
