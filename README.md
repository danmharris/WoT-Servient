# WoT Servient

The aim of this project is to create a network that provides interopability that will work with new devices and legacy IoT devices. The network will follow (as closely as possible) the reccomendation being developed by [W3](https://www.w3.org/WoT/WG/).

## Services
### Adapter
Produces virtual things which interface with devices not supporting WoT. Note: requires Docker network to be host

## Installation
The services are provided as Docker images and all run an HTTP server on port 8000.

Config is read from `/opt/wot/config` so custom config needs to be mounted here.
