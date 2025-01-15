# UniFi Network API Documentation

## Device Information

### Get Device Info
`GET /api/s/{site}/stat/device/{mac}`

#### Parameters
- `site` - Site name
- `mac` - Device MAC address

#### Response Example
json
{
"data": [
{
"mac": "00:00:00:00:00:00",
"model": "U7PG2",
"type": "uap",
"version": "4.0.66.10832"
}
]
}

### Update Device Settings
`PUT /api/s/{site}/rest/device/{mac}`

#### Parameters
- `site` - Site name
- `mac` - Device MAC address
- `name` - Device name (optional)
- `led_override` - LED override setting (optional)

#### Request Example
json
{
"led_override": "on",
"name": "My Access Point"
}

### Restart Device
`POST /api/s/{site}/cmd/devmgr/restart`

#### Parameters
- `site` - Site name
- `mac` - Device MAC address

#### Request Example
json
{
"mac": "00:00:00:00:00:00",
"cmd": "restart"
}

## Sites

### List Sites
`GET /api/self/sites`

#### Response Example
json
{
"data": [
{
"desc": "Default",
"name": "default"
}
]
}

## Clients

### Get Client Info
`GET /api/s/{site}/stat/sta/{mac}`

#### Parameters
- `site` - Site name
- `mac` - Client MAC address

#### Response Example

Example
json
{
"data": [
{
"mac": "00:00:00:00:00:00",
"hostname": "client-device",
"ip": "192.168.1.100"
}
]
}


## About Application

### Get Version Info
`GET /api/s/{site}/self`

#### Parameters
- `site` - Site name

#### Response Example
json
{
"version": "7.3.83"
}

---
**Note**: All API endpoints require proper authentication via API key. Response examples are simplified for documentation purposes.
