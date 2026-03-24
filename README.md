# HiTemp Water Heater Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/victor987/hitemp.svg)](https://github.com/victor987/hitemp/releases)

Home Assistant custom integration for HiTemp (Indol PV300) heat pump water heaters using the Aquatemp/linked-go cloud API.

## Features

- **Climate Control**: Full thermostat control with temperature setting and preset modes (Eco, Hybrid, Fast, Intelligent)
- **Temperature Sensors**: 8 temperature sensors (ambient, bottom, top, coil, suction, solar, discharge, display)
- **Status Monitoring**: Binary sensors for compressor, heater, defrost, and other operating states
- **Runtime Tracking**: Compressor and booster runtime counters
- **Advanced Settings**: 200+ configuration parameters for fine-tuning your water heater
- **Multi-Device Support**: Control multiple water heaters from one account

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add this repository URL: `https://github.com/victor987/hitemp`
5. Select category: "Integration"
6. Click "Add"
7. Search for "HiTemp Water Heater" in HACS
8. Click "Download"
9. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub releases](https://github.com/victor987/hitemp/releases)
2. Copy the `custom_components/hitemp` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

### Prerequisites

**Important**: You must create a dedicated account for this integration. The same account cannot be used simultaneously in the HiTemp mobile app and Home Assistant due to API limitations.

1. Create a new account in the HiTemp mobile app
2. Share your water heater device with the new account
3. Use the new account credentials in Home Assistant

### Setup

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "HiTemp Water Heater"
4. Enter your dedicated account email and password
5. Click **Submit**

The integration will automatically discover all water heaters associated with your account.

## Options

After setup, click **Configure** on the integration to set:

- **Power meter device**: Select a device (e.g. Zigbee smart plug) that monitors the water heater's power consumption. Its energy and power sensors will be mirrored under the water heater device and used for COP calculation and heating detection.

## Entities

### Climate

- **Water Heater**: Main climate entity with:
  - Current temperature (average of top and bottom sensors)
  - Target temperature control (38-75°C)
  - Preset modes: Eco, Hybrid, Fast, Intelligent
  - On/Off control
  - Heating state detection via power meter (>100W) or fan RPM fallback
- **Minimum Thermostat**: Virtual thermostat that maintains a minimum tank temperature by adjusting R01

### Sensors

**Temperature Sensors:**
- Ambient, bottom, top, coil, suction, solar, discharge, display temperatures

**Computed Sensors:**
- Precise temperature: avg(T02, T03) when within configurable threshold
- Temperature difference (T02 - T01)
- Superheat (T05 - T04): refrigerant state at compressor inlet
- Condenser approach (T07 - T02): condenser heat transfer efficiency
- Lift (T02 - T04): temperature the heat pump works against
- Energy stored (max/min/precise): tank thermal energy based on top, bottom, or average temperature
- COP: coefficient of performance (requires power meter device)
- Power: mirrored from configured power meter device
- Energy: mirrored from configured power meter device

**Operating Data:**
- Compressor runtime (hours)
- Booster runtime (hours)
- Fan RPM
- WiFi signal strength
- EEV position
- Various status counters

### Binary Sensors

- Compressor, electric heater, defrost status
- 4-way valve, fan high/low speed, solar pump
- WiFi connectivity

### Number Entities (Configuration)

150+ writable parameters organized by category:
- **Disinfection**: Temperature, duration, interval
- **Defrost**: Start/end temps, duration, mode
- **Compressor**: Cycle times, delays, frequency settings
- **EEV**: Superheat, position settings
- **Fan**: Speed, temperature thresholds
- **Heater**: Power level, operation mode
- **Solar**: Pump control, temperature thresholds
- **Main Settings**: Target temps, hysteresis, operation modes
- **Thresholds**: Precise temperature threshold (°C), energy stored threshold (kWh)

### Time / Date / Datetime Entities

- Timer 1/2 start and end times
- Disinfection start time, night decrease start/end
- Timer date
- Device time

### Switches

- Power on/off
- Booster (electric heater) on/off

### Fan

- Fan speed control (off, speed 1-5)

## Parameter Codes

All entities that correspond to device parameters include a `code` attribute showing the internal parameter code (e.g., "T01", "R01", "O01"). This is useful for advanced users and troubleshooting.

Example:
```yaml
sensor.water_heater_bottom_temperature:
  state: 45.5
  attributes:
    code: T02
```

## API Information

This integration uses the Aquatemp/linked-go cloud API:
- Base URL: `https://cloud.linked-go.com:449/crmservice/api`
- Product ID: `1245226668902080512`
- Update interval: 30 seconds

## Troubleshooting

### Authentication Errors

If you see "Invalid email or password" errors:
1. Verify your credentials are correct
2. Ensure you're using a dedicated account (not shared with the mobile app)
3. Try logging out of the mobile app completely

### Connection Issues

If entities show as unavailable:
1. Check your internet connection
2. Verify the device shows as "ONLINE" in the mobile app
3. Check Home Assistant logs for error messages

### Device Not Discovered

If your device doesn't appear:
1. Ensure the device is shared with the account you're using
2. Check that the device appears in the device list in the mobile app
3. Try removing and re-adding the integration

## Known Limitations

- One account can only be logged in to one location at a time (mobile app OR Home Assistant)
- Cloud-based polling only (no local API available)
- 30-second update interval
- Some parameters may be model-specific and not apply to all units

## Support

For issues, feature requests, or questions:
- [Open an issue on GitHub](https://github.com/victor987/hitemp/issues)
- Check existing issues for solutions

## Credits

Developed by reverse-engineering the HiTemp mobile app API.

## License

This project is provided as-is for personal use.
