#!/usr/bin/env bash
apt update && apt install -y git python3-venv python3-dev autoconf build-essential libffi-dev libssl-dev redis-server
python3 -m venv /opt/wot-network
source /opt/wot-network/bin/activate
pip install wheel
pip install -r $(dirname $0)/requirements.txt
pip install $(dirname $0)
cp -r $(dirname $0)/etc/systemd/system/* /etc/systemd/system/
cp $(dirname $0)/etc/wot-network.ini /etc/
