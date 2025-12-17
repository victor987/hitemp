# HiTemp Water Heater Integration

Control your HiTemp (Indol PV300) heat pump water heater from Home Assistant.

## Features

- **Climate Entity**: Full thermostat control with temperature setting and preset modes
- **8 Temperature Sensors**: Monitor ambient, bottom, top, coil, suction, solar, discharge, and display temperatures
- **Operating Status**: Binary sensors for compressor, heater, defrost, and more
- **Advanced Configuration**: 200+ adjustable parameters for fine-tuning
- **Multi-Device Support**: Control multiple water heaters from one account

## Important Setup Note

**You must create a dedicated account for this integration.** The same account cannot be logged into both the HiTemp mobile app and Home Assistant simultaneously due to API limitations.

### Setup Steps

1. Create a new account in the HiTemp mobile app
2. Share your water heater device with the new account (in the app settings)
3. Use the new account credentials when setting up this integration in Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "HiTemp Water Heater"
4. Enter your dedicated account email and password

## Entities Created

### Climate
- Water heater thermostat with preset modes: Eco, Hybrid, Fast, Intelligent

### Sensors
- 8 temperature sensors
- Compressor/booster runtime counters
- Compressor speed
- WiFi signal strength
- EEV position and various status sensors

### Binary Sensors
- Power, compressor, heater, defrost status
- 4-way valve, fan speeds, solar pump
- WiFi connectivity

### Number Entities
- Disinfection settings (temperature, duration, schedule)
- Defrost configuration
- Compressor cycle settings
- Fan and frequency controls
- And 150+ more advanced parameters

### Switch
- Power on/off control

## Notes

- Cloud-based polling every 30 seconds
- All entities include a `code` attribute showing the internal parameter code
- Some parameters may be model-specific
