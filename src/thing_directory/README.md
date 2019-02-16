# Thing Directory
A resource directory which contains thing descriptions of all the things found on the network that can be interacted with. This integrates with the proxy to rewrote URLs in thing descriptions on registration to go through the proxy.

## API
### `POST /things/register`
Register a given thing on the directory by providing its thing description
#### Data
The thing description to be parsed and added
```json
{
    "id": "urn:dev:wot:com:example:servient:lamp",
    "name": "MyLampThing",
    "description" : "MyLampThing uses JSON serialization",
    "securityDefinitions": {"psk_sc":{"scheme": "psk"}},
    "security": ["psk_sc"],
    "properties": {
        "status": {
            "description" : "Shows the current status of the lamp",
            "type": "string",
            "forms": [{
                "href": "coaps://mylamp.example.com/status"
            }]
        }
    },
    "actions": {
        "toggle": {
            "description" : "Turn on or off the lamp",
            "forms": [{
                "href": "coaps://mylamp.example.com/toggle"
            }]
        }
    },
    "events": {
        "overheating": {
            "description" : "Lamp reaches a critical temperature (overheating)",
            "data": {"type": "string"},
            "forms": [{
                "href": "coaps://mylamp.example.com/oh"
            }]
        }
    }
}
```
#### Returns
* 201: The thing has been successfully registered on the directory
```json
{
    "id": "abc123"
}
```
* 504: The directory could not reach the proxy to add endpoints
```json
{
    "message": "Could not reach proxy"
}
```

### `GET /things/query`
Query the directory based on a property (e.g. group)
#### Params
* groups: Comma separated list of groups, in an OR configuration `?groups=livingroom,kitchen`
#### Returns
* 200: Object of thing descriptions matching the criteria, keyed by UUID

### `GET /things/<uuid>`
Retrieves the thing description *except* for interactions
#### Returns
* 200: The schema for the requested uuid
```json
{
    "id": "urn:dev:wot:com:example:servient:lamp",
    "name": "MyLampThing",
    "description" : "MyLampThing uses JSON serialization",
    "securityDefinitions": {"psk_sc":{"scheme": "psk"}},
    "security": ["psk_sc"]
}
```
* 404: The UUID is not present in the database
```json
{
    "message": "Thing not found"
}
```

### `GET /things/<uuid>/{properties,actions,events}`
Retrieves the thing description for the given interaction
#### Returns
* 200: The schema for the requested uuid interaction
```json
{
    "{properties,actions,events}": {
        "interaction": {
            "forms": [{
                "href": "http://example.com"
            }]
        }
    }
}
```

### `DELETE /things/<uuid>`
Removes a thing from the directory
### Returns
* 200: The thing has successfully been removed
```json
{
    "message": "Deleted"
}
```

### `POST /things/<uuid>/groups`
Add a group to a thing description for future querying
#### Data
```json
{
    "group": "Living room"
}
```
#### Returns
* 200: Group was successfully added
```json
{
    "message": "updated"
}
```

### `DELETE /things/<uuid>/groups/<group>`
Remove the thing from a given group
### Returns
* 200: Group was successfully removed
```json
{
    "message": "group removed"
}
```
