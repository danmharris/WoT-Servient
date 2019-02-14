# Proxy
This is to be used as cache for properties read on various things. As they are low powered and resource constrained, it is unwise to have them requested constantly when they can be stored in a cache (Redis is used in this case)

## API
### `POST /proxy/add`
Adds a new endpoint to the service
#### Data
```json
{
    "url": "http://example.com"
}
```
#### Returns
* 201: The endpoint was successfully added
```json
{
    "uuid": "abc123"
}
```

### `GET /proxy/<uuid>`
Make a request on the proxy
#### Returns
* 200: Either the data from a request made to the thing *or* data retrieved from the cache, in whatever form is returned by the thing
* 404: The endpoint could not be found (locally)
```json
{
    "message": "Endpoint not found"
}
```
* 504: The proxy could not connect to the thing
```json
{
    "message": "Cannot reach thing"
}
```

### `GET /proxy/<uuid>/details`
Get the details about that endpoint (e.g. its true URL)
#### Returns
* 200: The details for the endpoint
```json
{
    "url": "http://example.com"
}
```

### `PUT /proxy/<uuid>`
Update details about the endpoint
#### Data
```json
{
    "url": "http://test.xyz"
}
```
#### Returns
* 200: Endpoint updated
```json
{
    "message": "Updated"
}
```
