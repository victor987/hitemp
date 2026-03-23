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

## Entities

### Climate

- **Water Heater**: Main climate entity with:
  - Current temperature (average of top and bottom sensors)
  - Target temperature control (38-75°C)
  - Preset modes: Eco, Hybrid, Fast, Intelligent
  - On/Off control

### Sensors

**Temperature Sensors:**
- Ambient temperature
- Bottom temperature
- Top temperature
- Coil temperature
- Suction temperature
- Solar temperature
- Discharge temperature
- Display temperature

**Operating Data:**
- Compressor runtime (hours)
- Booster runtime (hours)
- Fan RPM
- WiFi signal strength
- EEV position
- Various status counters

### Binary Sensors

- Power status
- Compressor running
- Electric heater running
- Defrost mode
- 4-way valve
- Fan high/low speed
- Solar pump
- WiFi connectivity

### Number Entities (Configuration)

200+ writable parameters organized by category:
- **Disinfection**: Temperature, duration, schedule, interval
- **Defrost**: Start/end temps, duration, mode
- **Compressor**: Cycle times, delays, frequency settings
- **EEV**: Superheat, position settings
- **Fan**: Speed, temperature thresholds
- **Heater**: Power level, operation mode
- **Solar**: Pump control, temperature thresholds
- **Main Settings**: Target temps, hysteresis, operation modes
- **Timers**: Schedule configuration

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
