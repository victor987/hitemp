# Bug: M06 and M17 entities never update in Home Assistant

## Problem

`number.water_heater_mode_setting_m06` has been stuck at 0.0 for over a month, even when the booster (electric heater) is actively running at >1500W with M06=1 confirmed via direct API calls. `sensor.water_heater_fan_status` (M17) has the same problem — always 0 even when fan is running at speed 5.

Other entities (temperatures T01-T07/T10, Power, mode_real, R01, O29, etc.) update normally.

## What we verified (2026-03-23)

### API returns correct values via direct calls

Using `hitemp2@sipao.net` credentials and `api_explore/params.py`:

- M06 reads 0 when booster off, 1 when on
- M17 reads 0-5 matching fan speed in the app
- We successfully wrote M06=1 (booster turned on, confirmed in app and by power meter)
- We successfully wrote M17=1-5 (fan speed changed, confirmed in app)
- A 152-code batch call (same as HA integration uses) returned all 152 codes including M06 and M17 with correct values. No drops.

### M06 write behavior

- 1 = On (confirmed via app + power meter)
- 2 = Off (value settles to 0 after a few seconds)
- 0 = Does NOT turn off — reverts to 1 within seconds

### M17 write behavior

- 0 = Fan off
- 1-5 = Fan speed (confirmed via app)
- Compressor running overrides physical fan to max, but M17 value stays

### Parameter scans

7 full scans taken in different states (all stored in `api_explore/query_results_*.txt`):

| File | State | M06 | M17 |
|------|-------|-----|-----|
| `query_results_fan_off.txt` | Idle | 0 | 0 |
| `query_results_fan_on_3.txt` | Fan speed 3 | 0 | 3 |
| `query_results_fan_on_4.txt` | Fan speed 4 | 0 | 4 |
| `query_results_fan_on_5.txt` | Fan speed 5 | 0 | 5 |
| `query_results_eheater_on.txt` | Booster on | 1 | 0 |
| `query_results_compressor_on.txt` | Compressor on | 0 | 0 |
| `query_results_compressor_eheater_on.txt` | Compressor + booster | 1 | 0 |

Values are correct in every scan. The API is not the problem.

## Integration code path

1. `coordinator.py:_async_update_data()` (line 76) calls `self._client.read_params(device_code, ALL_PARAMS)` every 30s
2. `api.py:read_params()` (line 128) POSTs all 152 codes to `/app/device/getDataByCode`, returns `{code: {value, rangeStart, rangeEnd}}`
3. Stored in `self.data[device_code]["_params"]`
4. `number.py:native_value` (line 146) calls `self.coordinator.get_device_param(device_code, param_code)` which returns `self.data[device_code]["_params"][param_code]["value"]`
5. Value cast to `float()` and returned

The entity extends `CoordinatorEntity` which calls `async_write_ha_state()` on every coordinator update. `native_value` is a property re-evaluated each cycle. No local caching.

## Debugging steps

### 1. Verify what the API returns during a live poll cycle

Add this temporary logging in `coordinator.py` after line 102 (`data[device_code]["_params"] = params`):

```python
_LOGGER.warning(
    "POLL DEBUG %s: M06=%s M17=%s Power=%s T02=%s (%d params)",
    device_code,
    params.get("M06"),
    params.get("M17"),
    params.get("Power"),
    params.get("T02", {}).get("value"),
    len(params),
)
```

Then:
- Turn booster ON in the app
- Wait 60+ seconds (2 poll cycles)
- Check HA logs for the WARNING lines

If M06 shows `{'value': '0', ...}` while the app shows booster ON, the API is returning stale data to this account/session.

If M06 shows `{'value': '1', ...}` but the entity still shows 0.0, the problem is in HA entity state propagation.

### 2. Check for stale entity registry entries

The unique_id format is `{device_code}_{param_code}`, e.g. `0C7FEDCE86BF_M06`. If this unique_id was ever registered under a different platform (sensor vs number), HA may be confused.

```bash
grep -i "M06\|M17\|fan_status\|mode_setting" .storage/core.entity_registry
```

Look for duplicate entries with the same `unique_id` but different `platform` values.

### 3. Check which account the integration uses

The test scripts use `hitemp2@sipao.net`. Verify the HA config:

```bash
grep -r "sipao\|hitemp" .storage/core.config_entries
```

### 4. Direct API test from HA host

Run this on the HA instance using the same credentials the integration uses:

```python
import asyncio, hashlib, aiohttp

async def test():
    async with aiohttp.ClientSession() as s:
        # USE THE SAME EMAIL/PASSWORD AS THE HA INTEGRATION
        pwd = hashlib.md5(b"PUT_PASSWORD_HERE").hexdigest()
        async with s.post(
            "https://cloud.linked-go.com:449/crmservice/api/app/user/login",
            headers={"Content-Type": "application/json; charset=utf-8"},
            json={"userName": "PUT_EMAIL_HERE", "password": pwd},
            ssl=False
        ) as r:
            token = (await r.json())["objectResult"]["x-token"]

        async with s.post(
            "https://cloud.linked-go.com:449/crmservice/api/app/device/getDataByCode",
            headers={"Content-Type": "application/json; charset=utf-8", "x-token": token},
            json={"deviceCode": "0C7FEDCE86BF", "protocalCodes": ["M06", "M17", "T02", "Power"]},
            ssl=False
        ) as r:
            for item in (await r.json()).get("objectResult", []):
                print(f"{item['code']} = {item.get('value')}")

asyncio.run(test())
```

Run this while booster is ON and fan is at speed 5. If M06 shows 0 here but 1 via `hitemp2@sipao.net`, it's an account-level issue.

### 5. Check if the entity state is actually updating but display is stale

In Developer Tools > States, search for `number.water_heater_mode_setting_m06`. Check:
- `state` field value
- `last_changed` timestamp — if old, entity value hasn't changed (always 0.0)
- `last_updated` timestamp — if recent, the coordinator IS running and updating the entity (just always with value 0.0)

### 6. Confirm the coordinator poll is running

Check any temperature sensor (e.g. `sensor.water_heater_bottom_temperature`). If `last_updated` is recent and values change, the coordinator is polling and the API connection works. The question then becomes: why do some params update (temperatures) and others don't (M06, M17)?

## Recent code changes affecting these entities

- `const.py`: M06 now excluded from `WRITABLE_NUMBER_PARAMS` (it's a switch now)
- `const.py`: M17 changed from `writable=False` to `writable=True, min=0, max=5`, excluded from both `NUMERIC_SENSOR_PARAMS` and `WRITABLE_NUMBER_PARAMS` (it's a fan entity now)
- `switch.py`: New `HiTempBoosterSwitch` for M06 (writes 1=on, 2=off)
- `fan.py`: New `HiTempFan` for M17 (writes 0-5)
- `__init__.py`: Added `Platform.FAN`

## Resolution (2026-03-31)

Issue resolved after v1.7.0 deployment. M06 and M17 now update correctly — changes made in the app are reflected in HA. Root cause was not definitively identified; likely resolved by one of the code changes in v1.5.0–v1.7.0 (entity restructuring, bitmask parsing, or coordinator updates).

After deploying these changes, the old `number.water_heater_mode_setting_m06` and `sensor.water_heater_fan_status` entities will become orphaned. They should be manually deleted from the entity registry.

## Key files

| File | What | Lines |
|------|------|-------|
| `coordinator.py` | Polling logic | 76-116 |
| `api.py` | API client, `read_params()` | 128-176 |
| `number.py` | Number entity, `native_value` | 146-154 |
| `sensor.py` | Sensor entity, `native_value` | 170-180 |
| `const.py` | `ALL_PARAMS` list | 308 |
| `const.py` | M06 definition | 181 |
| `const.py` | M17 definition | 188 |
| `switch.py` | Booster switch (new) | entire file |
| `fan.py` | Fan entity (new) | entire file |
