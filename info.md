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
- Minimum thermostat for maintaining minimum tank temperature

### Sensors
- 8 temperature sensors
- Computed: precise temperature, superheat, condenser approach, lift, temperature difference
- Energy stored (max/min/precise), COP (4h rolling window, precise + bottom variants)
- Power and energy (mirrored from configured power meter)
- Compressor/booster runtime counters, fan RPM, WiFi signal, EEV position

### Binary Sensors
- Compressor, heater, defrost status
- 4-way valve, fan speeds, solar pump, WiFi connectivity

### Number Entities
- 150+ writable configuration parameters
- Precise temperature and energy stored thresholds

### Time / Date / Datetime
- Timer 1/2 start/end times, disinfection/night decrease times
- Timer date, device time

### Switches
- Power on/off
- Booster (electric heater) on/off

### Fan
- Fan speed control (off, speed 1-5)

## Options

After setup, configure a **power meter device** (e.g. Zigbee smart plug) for COP calculation and heating detection.

## Notes

- Cloud-based polling every 30 seconds
- All entities include a `code` attribute showing the internal parameter code
- Some parameters may be model-specific
