# Bug Analysis: Energy Stored Sensor Not Updating

## Problem Statement
The Energy stored sensor (`sensor.water_heater_energy_stored`) was not updating its value or attributes, even though the T02 sensor from aqua_temp integration was updating correctly.

## Root Cause
Empty string handling in numeric sensors causes setup errors. **Whether this fully explains the Energy stored issue is uncertain** - see "Remaining Uncertainty" section below.

### Technical Details

1. **API Behavior**:
   - The HiTemp API returns empty strings (`''`) for some parameters that don't have values
   - Examples: `T11`, `T12`, `O01`-`O06`, `S01`-`S06`, etc.
   - From logs: `{'code': 'T11', 'value': '', 'dataType': '', ...}`

2. **Sensor Creation**:
   - `NUMERIC_SENSOR_PARAMS` includes `T11` ("Protection count") and `T12` ("EEPROM storage count")
   - These sensors have `state_class=MEASUREMENT` (numeric sensors)
   - When hitemp tries to create these sensors during setup, they have empty string values

3. **The Bug**:
   ```python
   # OLD CODE (sensor.py:170-179)
   @property
   def native_value(self) -> StateType:
       value = self.coordinator.get_device_param(self._device_code, self._param_code)
       if value is not None:
           try:
               return float(value)
           except (ValueError, TypeError):
               return value  # ← Returns empty string!
       return None
   ```

   - When `value = ''`, it's not None, so code enters the if block
   - `float('')` raises `ValueError`
   - Exception handler returns the empty string as-is
   - Home Assistant validates sensor values during setup
   - Sensors with `state_class=MEASUREMENT` **must** have numeric values or None
   - Empty string is rejected → **specific entities fail to be added**

4. **Error Logs** (from home-assistant_2026-01-04T22-18-55.905Z.log):
   ```
   2026-01-04 20:09:08.188 ERROR (MainThread) [homeassistant.components.sensor]
   Error adding entity sensor.water_heater_protection_count for domain sensor with platform hitemp
   Traceback (most recent call last):
     File "/usr/src/homeassistant/homeassistant/components/sensor/__init__.py", line 684, in state
       numerical_value = int(value)
   ValueError: invalid literal for int() with base 10: ''
   ```

5. **What Actually Happens**:
   - Error logs show: `Error adding entity sensor.water_heater_protection_count`
   - Error logs show: `Error adding entity sensor.water_heater_eeprom_storage_count`
   - These specific entities (T11, T12) fail to be added
   - BUT: Other entities ARE added (WiFi sensor warning appears after these errors)
   - The sensor platform continues, individual failures don't stop other entities

6. **Observation from Logs**:
   - No hitemp coordinator logs visible (only aqua_temp shows updates)
   - However, hitemp uses DEBUG level logging, which is not enabled by default
   - Cannot definitively prove coordinator isn't running from INFO level logs

## Why It Was Confusing

1. **Dual Integration Setup**:
   - User has both `aqua_temp` and `hitemp` integrations installed
   - aqua_temp was working fine (updating every ~5 minutes)
   - Only hitemp was broken

2. **Symptom Misdiagnosis**:
   - Initially thought: "Energy stored sensor becomes unavailable after hours"
   - Then thought: "Platform completely failed due to T11/T12 errors"
   - Reality: Some sensors fail (T11, T12) but others are added; unclear if coordinator runs
   - T02 sensor from aqua_temp worked fine, confusing which integration's sensors were updating

3. **Lack of Visibility**:
   - After the initial setup errors, no more hitemp logs at INFO level
   - Hitemp coordinator uses DEBUG level logging
   - Cannot determine if coordinator is running without enabling DEBUG

## Remaining Uncertainty

**What we know for certain:**
1. T11 and T12 sensors fail to be added due to empty string values
2. The API returns empty strings for these parameters
3. The fix will prevent these specific errors

**What we're uncertain about:**
1. Whether these errors affect other sensors (Energy stored uses T02, not T11/T12)
2. Whether the coordinator is actually running or not (DEBUG logs not visible)
3. Whether the original "unavailable after hours" issue is the same as "not updating"
4. User reported "energy stored is still available" after v1.2.9 - did something change?

**Possible alternative explanations:**
1. Coordinator might be running but DEBUG logs not visible at INFO level
2. Energy stored sensor might work but extra_state_attributes caching issue
3. Frontend might not be refreshing the attribute display

## The Fix

```python
# NEW CODE (sensor.py:170-180)
@property
def native_value(self) -> StateType:
    value = self.coordinator.get_device_param(self._device_code, self._param_code)
    # Treat empty strings as None (API returns '' for unavailable parameters)
    if value is not None and value != '':
        try:
            return float(value)
        except (ValueError, TypeError):
            return value
    return None
```

**Change**: Added `and value != ''` check before attempting conversion.

**What this definitely fixes:**
- T11 (Protection count) and T12 (EEPROM storage count) sensors will no longer cause errors
- These sensors will show "Unknown" instead of crashing

**What this might fix:**
- If the entity creation errors were somehow affecting the coordinator or other sensors
- General robustness for any parameters that return empty strings

## Expected Behavior After Fix

1. **Sensor Platform**:
   - T11 and T12 sensors initialize without errors (showing "Unknown")
   - No more "Error adding entity" messages for these sensors

2. **Coordinator** (assuming it wasn't already working):
   - Should continue running as designed (every 30 seconds)
   - Enable DEBUG logging to verify: add `custom_components.hitemp: debug` to logger config

3. **Energy Stored Sensor** (uncertain):
   - If the fix resolves the issue, it should update every 30 seconds
   - If it doesn't, further investigation needed

## Verification Steps After Fix

After installing v1.3.0:

1. Reload hitemp integration in Home Assistant
2. Check logs for:
   - No "Error adding entity" messages for protection_count or eeprom_storage_count
   - Optionally enable DEBUG logging: add `custom_components.hitemp: debug` to configuration.yaml logger
3. Check Energy stored sensor:
   - Should show a value
   - T02_bottom attribute should match hitemp's T02 sensor value
   - Monitor for 5+ minutes to confirm updates
4. Check Development Tools → States:
   - `sensor.water_heater_energy_stored` should have a state
   - Attributes should include `T02_bottom` with current value
5. Compare hitemp vs aqua_temp:
   - Both should show similar T02 values
   - If hitemp sensors update while aqua_temp runs, coordinator is working

## Files Changed

- `custom_components/hitemp/sensor.py`: Fix empty string handling
- `custom_components/hitemp/manifest.json`: Bump version to 1.3.0

## Release Notes for v1.3.0

**BUG FIX**: Fixed issue where empty string values from API caused T11 (Protection count) and T12 (EEPROM storage count) sensors to fail during entity setup. These sensors now show "Unknown" instead of causing errors.

**Note**: If your hitemp sensors weren't updating, this fix may help. If issues persist, enable DEBUG logging for `custom_components.hitemp` to help diagnose.
