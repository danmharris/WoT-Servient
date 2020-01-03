# WoT Servient
[![Build Status](https://travis-ci.com/danmharris/WoT-Servient.svg?token=4oghhh56MPM4pzayFJhw&branch=master)](https://travis-ci.com/danmharris/WoT-Servient)

The aim of this project is to create a network that provides interopability that will work with new devices and legacy IoT devices. The network will follow (as closely as possible) the reccomendation being developed by [W3](https://www.w3.org/WoT/WG/).

## Services
### [Thing Directory](thing_directory/)
A resource directory which contains thing descriptions of all the things found on the network that can be interacted with. This integrates with the proxy to rewrote URLs in thing descriptions on registration to go through the proxy.

### [Proxy](src/proxy/)
This is to be used as cache for properties read on various things. As they are low powered and resource constrained, it is unwise to have them requested constantly when they can be stored in a cache (Redis is used in this case)

### [Protocol Bindings](binding/)
These wrap legacy IoT devices in a HTTP API that can be controlled by a WoT application. As well as this they produce a thing description for a given thing so that it can be discovered and its interactions used.

### [Other Common Modules](src/common/)
Modules which can be used across all of these services, such as wrappers for Shelve databases or utilities for generating thing descriptions

## Installation
These services have been bundled with setuptools and contain systemd units for allowing them to be started automatically on boot.

They can be installed by running `sudo ./install.sh`, which will install the services under a python venv in `/opt/wot-network`. The configuration file at `/etc/wot-network.ini` will then need updating.

Running this script provides the following systemd units:
* `wot-td.service`
* `wot-proxy.service`
* `wot-binding.service`
* `wot-coap-thing.service`

This also installs a command line utility, which can be found in `/opt/wot-network/bin/wot-cli`. This allos for generation of API keys and credentials to connect to IKEA products.
