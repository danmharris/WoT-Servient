# Binding Template
These wrap legacy IoT devices in a HTTP API that can be controlled by a WoT application. As well as this they produce a thing description for a given thing so that it can be discovered and its interactions used.

## TP-LINK API
This template makes use of the PYHS100 Python library to perform its functions. It exposes the following endpoints

### `GET /state`
Returns the current state of the smart device

#### Returns
* 200: The status of the device
```json
{
    "state": "ON|OFF"
}
```

### `POST /state`
Updates the state of the smart device

#### Data
```json
{
    "state": "ON|OFF"
}
```

#### Returns
* 200: Message saying the update was successful
```json
{
    "message": "Updated"
}
```

* 400: Invalid state was provided
```json
{
    "message": "Invalid option"
}
```

### `POST /toggle`
Inverts the state of the device

#### Returns
* 200: State update was successful
```json
{
    "message": "updated"
}
```

### `GET /emeter`
Returns the electric meter readings of a smart plug _if_ it is supported

#### Returns
* 200: Values retrieved from the device

```json
{
    "current": 0,
    "power": 0,
    "total": 0,
    "voltage": 0
}
```

## IKEA TRADFRI API
This requires an IKEA TRADFRI gateway to be installed and configured on the network. It then exposes the following endpoints with the devices stored on it.

### `GET /state`
Returns the current state of the device

#### Returns
* 200: State of the device
```json
{
    "state": 0|1
}
```

### `POST /state`
Updates the state of the device

### Data
```json
{
    "state": 0|1
}
```

### Returns
* 200: State was successfully updated
```json
{
    "message": "Updated"
}
```
