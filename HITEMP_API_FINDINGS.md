# HiTemp API Findings

## Device Information

- **Device**: Indol PV300 Heat Pump Water Heater
- **Device Code**: `0C7FEDCE00XX`
- **Product ID**: `1245226668902080512`
- **Serial Number**: `A022409123456`
- **App**: HiTemp (uses Aquatemp/linked-go cloud platform)

## API Connection

### Base URL
```
https://cloud.linked-go.com:449/crmservice/api
```

### Headers
```json
{
  "Content-Type": "application/json; charset=utf-8",
  "x-token": "<token_from_login>"
}
```

### Authentication

**Endpoint**: `POST /app/user/login`

**Request**:
```json
{
  "userName": "<email>",
  "password": "<md5_hash_of_password>"
}
```

**Response**:
```json
{
  "error_msg": "Success",
  "objectResult": {
    "x-token": "<session_token>",
    "userId": "<user_id>",
    ...
  }
}
```

The `x-token` from the response must be included in headers for all subsequent requests.

## Reading Device Data

### Get Device List

The device is found via shared devices endpoint (not regular device list).

**Endpoint**: `POST /app/device/getMyAppectDeviceShareDataList`

**Request**:
```json
{
  "productIds": ["1245226668902080512"],
  "toUser": "<user_id>",
  "pageIndex": 1,
  "pageSize": 999
}
```

**Response**: Returns array of device objects. See Device Metadata section below for fields.

### Get Device Data

**Endpoint**: `POST /app/device/getDataByCode`

**Request**:
```json
{
  "deviceCode": "0C7FEDCE00XX",
  "protocalCodes": ["Power", "mode_real", "R01", "T10", ...]
}
```

**Response**:
```json
{
  "error_msg": "Success",
  "objectResult": [
    {"code": "R01", "value": "50.0", "rangeStart": "38", "rangeEnd": "75"},
    {"code": "mode_real", "value": "2", "rangeStart": "0", "rangeEnd": "4"},
    ...
  ]
}
```

**Note**: Protocol codes are case-insensitive (`R01` and `r01` return same data).

## Setting Parameters

**Endpoint**: `POST /app/device/control`

**Request**:
```json
{
  "param": [
    {
      "deviceCode": "0C7FEDCE00XX",
      "protocolCode": "R01",
      "value": 50.0
    }
  ]
}
```

Multiple parameters can be set in a single request by adding more items to the `param` array.

**Response**:
```json
{
  "error_msg": "Success",
  "error_code": "0"
}
```

## Mode Mapping (Verified)

| mode_real | App Display | Notes |
|-----------|-------------|-------|
| 0 | Intelligent | ? |
| 1 | (unused) | Displays as Intelligent but not set by app |
| 2 | Eco | Heat pump only |
| 3 | Hybrid | Heat pump + electric element after 200 minutes if target temp not reached |
| 4 | Fast heating | Heat pump + electric element |

## Protocol Codes

See `DEVICE_PARAMETERS.md` for the full list of 138 parameters.

Key codes for basic control:

| Code | Description | Range/Values |
|------|-------------|--------------|
| `Power` | On/off | 0/1 |
| `mode_real` | Operating mode | 0-4 (see Mode Mapping) |
| `R01` | Target temperature | 38-75°C |
| `T10` | Current water temperature | Read-only |

## Local Control

The device uses an ESP-based controller:

- Hostname: `espressif`
- **Client-only mode**: No listening TCP/UDP ports
- Device connects outbound to cloud, does not accept local connections

