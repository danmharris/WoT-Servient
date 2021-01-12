# WoT Servient

The aim of this project is to create a network that provides interoperability
that will work with new devices and legacy IoT devices. The network will follow
(as closely as possible) the recommendation being developed by
[W3](https://www.w3.org/WoT/WG/).

## Installation
All services have corresponding docker containers and a docker-compose.yaml file
is provided to orchestrate all of them (including a Traefik reverse proxy).

So installing is a matter of cloning the repository, copying the
`.$service.env.example` files to `.$service.env.local` and then running
`docker-compose up -d`.

```
git clone https://github.com/danmharris/WoT-Servient.git /opt/wot
cd /opt/wot
cp .env.example .env.local
cp client/.env client/.env.local
docker-compose up -d
```

## Services
### Common Environment Variables

* `BASE_URI`: Base URI to API machine (defaults to
  system hostname)
* `DB_PATH`: Where to store the database (defaults to `/data`)

### Adapter
Produces virtual things which interface with devices not supporting WoT.
Note: requires Docker network to be host and runs on port 8000.

#### Environment Variables

* `ADAPTER_PLUGINS`: Comma-separated list of plugins to enable (available: "tplink")
* `ADAPTER_BASE_URI`: Sets the base property of all thing descriptions (defaults to
  system hostname)

### Grouper
Produces virtual things which perform one or more actions with other things.
This can be used to create presets/scenes or sequences.

#### Docker Volumes
* `/data`: Database folder

### Thing Directory
Collates things from a variety of sources and presents them as one list

#### Docker Volumes
* `/data`: Database folder

### Client
Vue.js single page application that interfaces with the API.

#### Environment Variables
File: `client/.env` (this uses `.env` instead of `.env.example`)

* `VUE_APP_API_BASE_URI`: Base to the API (defaults to `/api/v1`)
