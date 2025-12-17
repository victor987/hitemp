# Indol PV300 / HiTemp Device Parameters

**Device Code**: 0C7FEDCE00XX
**Product ID**: 1245226668902080512
**Last Updated**: 2024-12-13

## Query Verification

- Queried all codes A00-Z99 (2600 codes) + special codes + /00-/99 + numeric codes 0-9999
- **No timeouts or errors**
- **210 writable + 82 read-only = 292 total codes** (but most numeric codes are aliases)
- **Letters with data**: C, D, E, F, G, H, L, M, N, O, R, T + Power/Mode/mode_real + /01, /02
- **Letters with NO data**: A, B, I, J, K, P, Q, S, U, V, W, X, Y, Z (all return empty)
- **Case insensitive**: Uppercase (C01) and lowercase (c01) return the same parameter
- **Numeric aliases**: 86 parameters have numeric aliases (71 writable + 15 read-only) shown in "Alt Code" column

## Legend

**Writability**:
- `CONFIRMED` - We tested writing to this parameter
- `LIKELY` - Has numeric range (implies writable)
- `BITMASK` - 16-char binary string, likely writable flags
- `READ-ONLY` - No range, appears to be sensor/status

**User Confirmed**: Parameters where the purpose has been verified by testing

---

## / Codes - Output Configuration

| Code | Value | Range | Writability | Likely Purpose | User Confirmed | Unit | Possible Values |
|------|-------|-------|-------------|----------------|----------------|------|-----------------|
| /01 | 0 | 0-2 | LIKELY | Usage of OUT 05 | Aquatemp | - | 0/1/2 |
| /02 | 0 | 0-3 | LIKELY | Usage of OUT 06 | Aquatemp | - | 0/1/2/3 |

---

## Special Control Parameters

| Code | Alt Code | Value | Range | Writability | Likely Purpose | User Confirmed | Unit | Possible Values |
|------|----------|-------|-------|-------------|----------------|----------------|------|-----------------|
| Power | 1011 | 1 | 0-1 | CONFIRMED | Power on/off | YES | - | 0=Off, 1=On |
| mode_real | 1013 | 2 | 0-4 | CONFIRMED | Operating mode | YES | - | 0=Intelligent, 1=unused, 2=Eco, 3=Hybrid, 4=Fast heating |
| Mode | 1012 | 2 | 0-7 | LIKELY | Operating mode (mirror) | Mirrors mode_real | - | |

---

## C Codes - Compressor/Cycle Settings

| Code | Alt Code | Value | Range | Writability | Likely Purpose | User Confirmed | Unit | Possible Values |
|------|----------|-------|-------|-------------|----------------|----------------|------|-----------------|
| C01 | | 0 | 0-120 | LIKELY | Delay timer minutes? | | min | |
| C02 | 1023 | 30 | 20-60 | LIKELY | Min cycle time? | | min | |
| C03 | 1024 | 90 | 30-120 | LIKELY | Max cycle time? | | min | |
| C05 | 1033 | 2073 | 0-65535 | LIKELY | Run time counter? | | - | |
| C06 | 1026 | 52 | 0-120 | LIKELY | Timer setting | | min | |
| C07 | 1029 | 50 | 0-120 | LIKELY | Timer setting | | min | |
| C08 | 1030 | 60 | 0-120 | LIKELY | Timer setting | | min | |
| C09 | 1031 | 0 | 0-120 | LIKELY | Timer setting | | min | |

---

## D Codes - Defrost Settings

| Code | Alt Code | Value | Range | Writability | Likely Purpose | User Confirmed | Unit | Possible Values |
|------|----------|-------|-------|-------------|----------------|----------------|------|-----------------|
| D01 | 1034 | -7.0 | -30 to 0 | LIKELY | Defrosting start | YES | °C | |
| D02 | 1035 | 13.0 | 0-30 | LIKELY | Defrosting end | YES | °C | |
| D03 | 1036 | 45 | 30-90 | LIKELY | Defrosting duration | Aquatemp | min | |
| D04 | 1037 | 4.0 | 1-20 | LIKELY | Longest duration of defrosting | Aquatemp | min | |
| D05 | 1038 | 44.0 | 0-4.00 | LIKELY | Shortest duration of defrosting | Aquatemp | min | |
| D06 | 1039 | 0 | 0-2 | LIKELY | Defrosting mode | Aquatemp | - | 0/1/2 modes |
| D07 | 1040 | 2.0 | -10 to 20 | LIKELY | Intelligent defrosting judgement | Aquatemp | °C | |
| D10 | 1042 | 0.0 | -30 to 5 | LIKELY | Low temp threshold | | °C | |
| D11 | 1043 | 10 | 5-30 | LIKELY | Duration setting | | min | |
| D12 | 1041 | 10.0 | 0-20 | LIKELY | Temp differential | | °C | |
| D13 | 1051 | -18.0 | -30 to 0 | LIKELY | Min operating temp | | °C | |

---

## E Codes - Electronic Expansion Valve Settings

| Code | Alt Code | Value | Range | Writability | Likely Purpose | User Confirmed | Unit | Possible Values |
|------|----------|-------|-------|-------------|----------------|----------------|------|-----------------|
| E01 | 1055 | 1 | 0-1 | LIKELY | EEV adjustment mode | Aquatemp | - | 0=Off, 1=On |
| E02 | 1056 | 7.0 | -20 to 20 | LIKELY | Target degree of superheat | Aquatemp | °C | |
| E03 | 1057 | 240 | 0-500 | LIKELY | Original position of EEV | Aquatemp | - | |
| E04 | 1058 | 100 | 0-500 | LIKELY | Minimal opening position of EEV | Aquatemp | - | |
| E05 | 1059 | 480 | 0-500 | LIKELY | Position of EEV for defrosting | Aquatemp | - | |
| E06 | 1060 | 0 | 0-480 | LIKELY | Timer setting | | - | |

---

## F Codes - Fan/Frequency Settings

| Code | Alt Code | Value | Range | Writability | Likely Purpose | User Confirmed | Unit | Possible Values |
|------|----------|-------|-------|-------------|----------------|----------------|------|-----------------|
| F01 | 1160 | 0 | 0-4 | LIKELY | Fan mode | | - | 0-4 modes? |
| F02 | 1161 | 0 | 0-1500 | LIKELY | Min frequency | | Hz | |
| F03 | 1162 | 0000000000000001 | - | BITMASK | Configuration flags | | - | 16-bit flags |
| F04 | 1163 | 830 | 0-1500 | LIKELY | Max frequency | | Hz | |
| F05 | 1164 | 300 | 0-1500 | LIKELY | Frequency setting | | Hz | |
| F06 | 1165 | 15.0 | 0-50 | LIKELY | Fan start temp | | °C | |
| F07 | 1166 | 35.0 | 0-50 | LIKELY | Fan max temp | | °C | |
| F09 | 1168 | 320 | 0-1500 | LIKELY | Frequency step | | Hz | |
| F10 | 1169 | 380 | 0-1500 | LIKELY | Frequency step | | Hz | |
| F11 | 1170 | 560 | 0-1500 | LIKELY | Frequency step | | Hz | |
| F12 | 1171 | 700 | 0-1500 | LIKELY | Frequency step | | Hz | |
| F13 | 1172 | 830 | 0-1500 | LIKELY | Frequency step | | Hz | |

---

## G Codes - Disinfection Settings

| Code | Alt Code | Value | Range | Writability | Likely Purpose | User Confirmed | Unit | Possible Values |
|------|----------|-------|-------|-------------|----------------|----------------|------|-----------------|
| G01 | 1046 | 60.0 | 30-70 | LIKELY | Disinfection target | YES | °C | |
| G02 | 1047 | 50 | 0-90 | LIKELY | Disinfection duration | YES | min | |
| G03 | 1048 | 0 | 0-23 | LIKELY | Disinfection start hour | YES | hour | |
| G04 | 1049 | 7 | 1-99 | LIKELY | Disinfection interval | YES | days | |

---

## H Codes - Heater/Heating Element Settings

| Code | Alt Code | Value | Range | Writability | Likely Purpose | User Confirmed | Unit | Possible Values |
|------|----------|-------|-------|-------------|----------------|----------------|------|-----------------|
| H01 | | 1 | 0-1 | LIKELY | Remember device status when power down | Aquatemp | - | 0=Off, 1=On |
| H03 | 1069 | 0 | 0-0 | LIKELY | Heating source | Aquatemp | - | |
| H07 | | 0 | 0-1 | LIKELY | Temperature unit | Aquatemp | - | 0=°C, 1=°F |
| H09 | | 0 | 0-1 | LIKELY | Heater option | | - | 0=Off, 1=On |
| H16 | 1068 | 6 | 0-10 | LIKELY | Heater power level? | | - | |
| H30 | 1076 | 1 | 1-255 | LIKELY | Device address | Aquatemp | - | |
| H31 | | 1 | 0-1 | LIKELY | Intelligent control mode | Aquatemp | - | 0=Off, 1=On |
| H32 | 1066 | 5 | 1-255 | LIKELY | Circle of submitting data to Cloud | Aquatemp | min | |
| H98 | 1074 | 2 | 2-3 | LIKELY | Adjustable range of target temperature | Aquatemp | - | 2 or 3 |
| H99 | | 0 | 0-1 | LIKELY | Compensate to the shown temp | Aquatemp | - | 0=Off, 1=On |

---

## L Codes - Legionella/Timer Schedule

| Code | Alt Code | Value | Range | Writability | Likely Purpose | User Confirmed | Unit | Possible Values |
|------|----------|-------|-------|-------------|----------------|----------------|------|-----------------|
| L02 | 1130 | 21 | 20-99 | LIKELY | Year (20XX) | | year | |
| L03 | 1131 | 1 | 1-12 | LIKELY | Month | | month | |
| L04 | 1132 | 1 | 1-31 | LIKELY | Day | | day | |
| L06 | | 0 | 0-23 | LIKELY | Timer 1 start hour | | hour | |
| L07 | | 0 | 0-59 | LIKELY | Timer 1 start minute | | min | |
| L08 | | 0 | 0-23 | LIKELY | Timer 1 end hour | | hour | |
| L09 | | 0 | 0-59 | LIKELY | Timer 1 end minute | | min | |
| L10 | | 0 | 0-23 | LIKELY | Timer 2 start hour | | hour | |
| L11 | | 0 | 0-59 | LIKELY | Timer 2 start minute | | min | |
| L12 | | 0 | 0-23 | LIKELY | Timer 2 end hour | | hour | |
| L13 | | 0 | 0-59 | LIKELY | Timer 2 end minute | | min | |
| L28 | | 0000000000000000 | - | BITMASK | Schedule flags | | - | 16-bit flags |
| L29 | 1143 | 1 | 0-255 | LIKELY | Timer config | | - | |
| L30 | | 0 | - | READ-ONLY | Status | | - | |
| L31 | 2075 | 124 | - | READ-ONLY | Status/counter | | - | |
| L32 | 2076 | 243 | - | READ-ONLY | Status/counter | | - | |

---

## M Codes - Mode/Time Settings

| Code | Alt Code | Value | Range | Writability | Likely Purpose | User Confirmed | Unit | Possible Values |
|------|----------|-------|-------|-------------|----------------|----------------|------|-----------------|
| M06 | 1014 | 0 | 1-2 | LIKELY | Unknown | | - | 1 or 2 |
| M07 | | 0 | 0-1 | LIKELY | Enable flag | | - | 0=Off, 1=On |
| M12 | 1152 | 26 | 0-59 | LIKELY | Device time minute | YES | min | |
| M13 | 1153 | 19 | 0-23 | LIKELY | Device time hour | YES | hour | |
| M14 | 1154 | 13 | 1-31 | LIKELY | Device time day | YES | day | |
| M15 | 1155 | 12 | 1-12 | LIKELY | Device time month | YES | month | |
| M16 | 1156 | 25 | 0-99 | LIKELY | Device time year (20XX) | YES | year | |
| M17 | | 0 | - | READ-ONLY | Fan status? | | - | |

---

## N Codes - Solar Settings

| Code | Alt Code | Value | Range | Writability | Likely Purpose | User Confirmed | Unit | Possible Values |
|------|----------|-------|-------|-------------|----------------|----------------|------|-----------------|
| N01 | | 0 | 0-1 | LIKELY | Sensor to control solar water pump | Aquatemp | - | 0=Off, 1=On |
| N02 | 1081 | 15 | 1-30 | LIKELY | Longest running time of solar water pump | Aquatemp | min | |
| N03 | 1082 | 20.0 | 0-20 | LIKELY | Temp hysteresis of solar water pump | Aquatemp | °C | |
| N04 | 1083 | 0 | 0-1 | LIKELY | Activate nighttime temp decreases mode | Aquatemp | - | 0=Off, 1=On |
| N05 | 1084 | 0 | 0-23 | LIKELY | Startup point of nighttime temp decreases | Aquatemp | hour | |
| N06 | 1085 | 6 | 0-23 | LIKELY | Shutdown point of nighttime temp decreases | Aquatemp | hour | |
| N07 | 1086 | 70.0 | 40-90 | LIKELY | Startup temp of decreasing solar water temp | Aquatemp | °C | |
| N08 | 1087 | 10.0 | 1-40 | LIKELY | Temp hysteresis of stopping decreasing | Aquatemp | °C | |
| N09 | 1088 | 68.0 | 50-90 | LIKELY | Solar water releasing temp | Aquatemp | °C | |
| N10 | 1089 | 50.0 | 50-90 | LIKELY | Shutdown temp of solar water pump | Aquatemp | °C | |
| N11 | 1090 | 0 | 0-1 | LIKELY | Working mode of solar water pump | Aquatemp | - | 0=Off, 1=On |

---

## O Codes - Operating Data (Read-Only)

| Code | Alt Code | Value | Range | Writability | Likely Purpose | User Confirmed | Unit | Possible Values |
|------|----------|-------|-------|-------------|----------------|----------------|------|-----------------|
| O01 | | - | - | READ-ONLY | Compressor | Aquatemp | - | |
| O02 | | - | - | READ-ONLY | Electrical heater | Aquatemp | - | |
| O03 | | - | - | READ-ONLY | 4-way valve | Aquatemp | - | |
| O04 | | - | - | READ-ONLY | Fan high speed | Aquatemp | - | |
| O05 | | - | - | READ-ONLY | Fan low speed | Aquatemp | - | |
| O06 | | - | - | READ-ONLY | Reserve/solar pump/solar valve pump | Aquatemp | - | |
| O07 | 2060 | 226 | - | READ-ONLY | EEV current position | Aquatemp | - | |
| O08 | 2061 | 504 | - | READ-ONLY | Accumulative running time of compressor | Aquatemp | h | |
| O09 | | 0 | - | READ-ONLY | Accumulative running time of booster | Aquatemp | h | |
| O10 | | - | - | READ-ONLY | 3V_DE | Aquatemp | - | |
| O11 | | - | - | READ-ONLY | MV_DE | Aquatemp | - | |
| O12 | | - | - | READ-ONLY | shutDown | Aquatemp | - | |
| O13 | | - | - | READ-ONLY | DTU&WIFI online status | Aquatemp | - | |
| O14 | | - | - | READ-ONLY | Defrost status | Aquatemp | - | |
| O15 | | - | - | READ-ONLY | High temp hot water stage | Aquatemp | - | |
| O18 | 2062 | 0 | - | READ-ONLY | Status | | - | |
| O19 | 2063 | 0 | - | READ-ONLY | Status | | - | |
| O20 | 2064 | 0 | - | READ-ONLY | Status | | - | |
| O21 | 2065 | -55 | - | READ-ONLY | Temp sensor? | | °C | |
| O22 | | 0 | - | READ-ONLY | Status | | - | |
| O23 | | 0 | - | READ-ONLY | Status | | - | |
| O24 | | 0 | - | READ-ONLY | Status | | - | |
| O25 | | 0 | - | READ-ONLY | Status | | - | |
| O26 | | 0 | - | READ-ONLY | Status | | - | |
| O27 | | 0 | - | READ-ONLY | Status | | - | |
| O28 | 2066 | 6.0 | - | READ-ONLY | Unknown | YES | - | |
| O29 | | 830 | - | READ-ONLY | Compressor speed | YES | Hz | |

---

## R Codes - Main Settings

| Code | Alt Code | Value | Range | Writability | Likely Purpose | User Confirmed | Unit | Possible Values |
|------|----------|-------|-------|-------------|----------------|----------------|------|-----------------|
| R01 | 1104 | 45.0 | 38-75 | CONFIRMED | Target | YES | °C | |
| R02 | | 0 | 0-3 | LIKELY | Sub-mode setting | | - | 0/1/2/3 |
| R03 | 1106 | 5.0 | 1-20 | LIKELY | Hysteresis of heat pump startup (bottom) | Aquatemp | °C | |
| R04 | | 0 | 0-1 | LIKELY | Enable R05 as setpoint of booster? | Aquatemp | - | 0=Off, 1=On |
| R05 | | 55.0 | 30-90 | LIKELY | Setpoint of booster | Aquatemp | °C | |
| R06 | 1109 | 200 | 0-90 | LIKELY | Booster startup delay | Aquatemp | min | |
| R07 | | 0 | 0-1 | LIKELY | Booster replaces heat pump? | Aquatemp | - | 0=Off, 1=On |
| R08 | 1111 | -5.0 | -20 to 10 | LIKELY | Ambient temp to activate booster to replace HP | Aquatemp | °C | |
| R09 | 1112 | 5.0 | 0-30 | LIKELY | Ambient temp to activate booster without delay | Aquatemp | °C | |
| R10 | 1113 | 25.0 | 10-40 | LIKELY | Ambient temp to activate booster with delay | Aquatemp | °C | |
| R11 | | 0 | 0-1 | LIKELY | Option flag | | - | 0=Off, 1=On |
| R12 | 1115 | -15.0 | -30 to -5 | LIKELY | Ambient temp of shutting down compressor compulsively | Aquatemp | °C | |
| R13 | 1116 | 0 | 0-5 | LIKELY | Mode/level setting | | - | 0-5 |
| R14 | 1117 | 45.0 | 38-78 | LIKELY | Target temp of second heating source | Aquatemp | °C | |
| R15 | 1118 | 78.0 | 55-80 | LIKELY | Maximal ambient temp of working compressor | Aquatemp | °C | |
| R16 | 1119 | 3 | 0-3 | LIKELY | Mode setting | | - | 0/1/2/3 |
| R17 | | 0 | 0-1 | LIKELY | Enable top sensor to control compressor? | Aquatemp | - | 0=Off, 1=On |
| R18 | 1121 | 3.0 | 1-20 | LIKELY | Hysteresis of heat pump startup (top) | Aquatemp | °C | |
| R19 | 1122 | 65.0 | 30-90 | LIKELY | Setpoint 1 of ambient temp to stop compressor | Aquatemp | °C | |
| R20 | | 55.0 | 30-90 | LIKELY | Setpoint 2 of ambient temp to stop compressor | Aquatemp | °C | |

---

## T Codes - Temperature Sensors

| Code | Alt Code | Value | Range | Writability | Likely Purpose | User Confirmed | Unit | Possible Values |
|------|----------|-------|-------|-------------|----------------|----------------|------|-----------------|
| T01 | 2019 | 17.0 | - | READ-ONLY | Ambient | Aquatemp | °C | |
| T02 | 2020 | 40.0 | - | READ-ONLY | Bottom  | Aquatemp | °C | |
| T03 | 2021 | 49.0 | - | READ-ONLY | Top | Aquatemp | °C | |
| T04 | 2022 | 8.0 | - | READ-ONLY | Coil | Aquatemp | °C | |
| T05 | 2023 | 14.0 | - | READ-ONLY | Suction | Aquatemp | °C | |
| T06 | 2024 | 20.0 | - | READ-ONLY | Solar | Aquatemp | °C | |
| T07 | 2028 | 59.0 | - | READ-ONLY | Discharge | | °C | |
| T08 | 2029 | 0000000000000000 | - | BITMASK | Sensor status flags | | - | 16-bit flags |
| T09 | 2030 | 37 | - | READ-ONLY | | | - | |
| T10 | | 49.0 | - | READ-ONLY | Value shown on APP/display | YES | °C | Main display temp |
| T11 | | - | - | READ-ONLY | Parameter out of range protection count | Aquatemp | - | |
| T12 | | - | - | READ-ONLY | EEPROM storage count | Aquatemp | - | |
| T20 | | 0 | - | READ-ONLY | Status | | - | |
| T21 | | 0 | - | READ-ONLY | Status | | - | |

---

## Numeric Codes

Numeric codes not yet identified as aliases. Codes with unique matches are documented in the "Alt Code" column of other sections.

### Writable Numeric Codes

| Code | Value | Range | Writability | Notes |
|------|-------|-------|-------------|-------|
| 1015 | 0 | 0-1 | LIKELY | |
| 1020 | 0 | 0-2 | LIKELY | |
| 1021 | 0 | 0-3 | LIKELY | |
| 1025 | 0 | 0-120 | LIKELY | |
| 1067 | 1 | 0-1 | LIKELY | |
| 1070 | 0 | 0-1 | LIKELY | |
| 1073 | 0 | 0-1 | LIKELY | |
| 1075 | 0 | 0-1 | LIKELY | |
| 1077 | 1 | 0-1 | LIKELY | |
| 1080 | 0 | 0-1 | LIKELY | |
| 1105 | 0 | 0-3 | LIKELY | |
| 1107 | 0 | 0-1 | LIKELY | |
| 1108 | 55.0 | 30-90 | LIKELY | |
| 1110 | 0 | 0-1 | LIKELY | |
| 1114 | 0 | 0-1 | LIKELY | |
| 1120 | 0 | 0-1 | LIKELY | |
| 1123 | 55.0 | 30-90 | LIKELY | |
| 1134 | 0 | 0-23 | LIKELY | |
| 1135 | 0 | 0-59 | LIKELY | |
| 1136 | 0 | 0-23 | LIKELY | |
| 1137 | 0 | 0-59 | LIKELY | |
| 1138 | 0 | 0-23 | LIKELY | |
| 1139 | 0 | 0-59 | LIKELY | |
| 1140 | 0 | 0-23 | LIKELY | |
| 1141 | 0 | 0-59 | LIKELY | |

### Read-Only Numeric Codes

| Code | Value | Writability | Notes |
|------|-------|-------------|-------|
| 1016 | 0 | READ-ONLY | |
| 1129 | 0000000000000000 | BITMASK | 16-bit flags |
| 1133 | 0000000000000000 | BITMASK | 16-bit flags |
| 1142 | 0000000000000000 | BITMASK | 16-bit flags |
| 1151 | 0000000000000000 | BITMASK | 16-bit flags |
| 1158 | 23205 | READ-ONLY | |
| 2011 | 1.2 | READ-ONLY | |
| 2012 | 569 | READ-ONLY | |
| 2013 | 1.1 | READ-ONLY | |
| 2014 | 570 | READ-ONLY | |
| 2025 | 56.0 | READ-ONLY | |
| 2026 | 0 | READ-ONLY | |
| 2027 | 0 | READ-ONLY | |
| 2050 | 0000000000100100 | BITMASK | 16-bit flags |
| 2051 | 0000000000000001 | BITMASK | 16-bit flags |
| 2057 | 0 | READ-ONLY | |
| 2058 | 0 | READ-ONLY | |
| 2059 | 0 | READ-ONLY | |
| 2068 | 0 | READ-ONLY | |
| 2069 | 0 | READ-ONLY | |
| 2070 | 0 | READ-ONLY | |
| 2071 | 0 | READ-ONLY | |
| 2074 | 0 | READ-ONLY | |
| 2085 | 0000000000000000 | BITMASK | 16-bit flags |

---

## Device Metadata Fields

When retrieving the device list via `POST /app/device/getMyAppectDeviceShareDataList`, each device object includes these metadata fields:

| Field | Example Value | Description |
|-------|---------------|-------------|
| `deviceStatus` | "ONLINE" | Online/offline status |
| `deviceCode` | "0C7FEDCE00XX" | Unique device identifier |
| `deviceId` | "1843824764494401234" | Internal device ID |
| `deviceNickName` | "Water heater" | User-assigned device name |
| `serialNumber` | "A022409123456" | Device serial number |
| `productId` | "1245226668902080512" | Product type identifier |
| `wifiSoftwareVer` | "V1.1" | WiFi module firmware version |
| `wifiSoftwareCode` | "82400511" | WiFi firmware code |
| `dtuCodeVersion` | "824005110011" | DTU firmware version |
| `dtuSignalIntensity` | "57" | WiFi signal strength (0-100) |
| `dtuMainboardComm` | "0" | Mainboard communication status |
| `dtuIccid` | "0C7FEDCE00XX" | ICCID (or device code fallback) |
| `dtuImeiMac` | "0C7FEDCE00XX" | IMEI/MAC (or device code fallback) |
| `lockState` | "1" | Device lock state |
| `isLock` | "0" | Lock status flag |
| `createTime` | "2024-10-09 09:24:15.0" | Device creation timestamp |
| `boundTime` | "2025-09-25 20:15:56.0" | When device was bound to account |
| `lastUpdateTime` | "2025-11-30 07:14:40.163" | Last data update timestamp |
| `email` | "email@example.com" | Associated email address |
| `nickName` | "email@example.com" | Account nickname |
| `dealersId` | "1590510928972091234" | Dealer ID |
| `userId` | "1970794807107221234" | Owner user ID |
| `shareId` | "1971217557951301234" | Share ID (for shared devices) |
| `reviewStatus` | "0" | Review/approval status |
| `orgId` | "1110" | Organization ID |
| `state` | "A" | Device state |
| `faultState` | false | Fault detection flag |
| `isFault` | false | Fault status |

---

## Notes

1. Values captured at specific moment - some change during operation
2. "Likely Purpose" is inferred from values/ranges - needs verification
3. Bitmask values (16 chars of 0/1) are configuration flags
4. Range "0-90" with value "200" suggests possible API inconsistency (R06)
5. Some parameters may be model-specific
6. **Alt Code**: Numeric aliases (1000-1999 series) that map to the same parameter as the letter code. Both codes work identically for reading/writing.

## API Usage

To read: `POST /app/device/getDataByCode` with `protocalCodes` array (not a typo)
To write: `POST /app/device/control` with `param` array containing `protocolCode` and `value`
