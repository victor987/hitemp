# HiTemp Integration - Entity List

Organized by the four sections shown on the HA device page. Within each section, rows are alphabetical by name.

History data queried from HA recorder on 2026-03-24 with `start_time=2020-01-01`, `significant_changes_only=false`. Earliest data from 2026-01-10. "Constant" means the non-unavailable/unknown state value has not changed within the observed period. Entry counts include unavailable transitions.

**Status column**: blank = active, `removed` = no entity created (param still fetched), `disabled` = entity exists but disabled by default.

---

## Controls

| Platform | Name | Code(s) | Precision | Notes | History | Status |
|---|---|---|---|---|---|---|
| switch | Booster | M06 | on/off | On=1 / Off=2 | constant: off (3 entries since 2026-03-23) | |
| fan | Fan | M17 | 5 speeds | Speed 0 (off) – 5 | constant: off (3 entries since 2026-03-23) | |
| climate | Minimum Thermostat | R01, T02, T03 | target 1°C, current 0.5°C | Virtual — keeps min(T02, T03) at target via R01 formula | constant: off (64303 entries since 2026-01-10, attr updates only) | |
| climate | (device name) | Power, mode_real, R01, T02, T03 | target 1°C, current 0.25°C | Main thermostat — avg(T02, T03), presets Eco/Hybrid/Fast/Intelligent | always heat (62621 entries, attr updates) | |
| switch | (device name) | Power | on/off | On/off | constant: on (39 entries since 2026-01-10) | disabled |

---

## Sensors

| Name | Code(s) | Platform | Precision | unique_id suffix | History | Status |
|---|---|---|---|---|---|---|
| Ambient temperature | T01 | sensor | 0.5°C | `_T01` | 16929 changes | |
| Bottom temperature | T02 | sensor | 0.5°C | `_T02` | 44893 changes | |
| COP | — | sensor | 0.01 | `_cop` | 39975 changes (pre-v1.8.0: per-interval) | |
| COP (bottom) | — | sensor | 0.01 | `_cop_bottom` | new in v1.8.0 | |
| Coil temperature | T04 | sensor | 0.5°C | `_T04` | 30718 changes | |
| Condenser approach | T07, T02 | sensor | 0.5°C (round 0.1) | `_condenser_approach` | 1147 changes | |
| Discharge temperature | T07 | sensor | 0.5°C | `_T07` | 39323 changes | |
| Display temperature | T10 | sensor | 0.5°C | `_T10` | 26607 changes | |
| Energy | — | sensor | 0.01 kWh | `_energy_meter` | 17 changes (since 2026-03-24) | |
| Energy stored | T02, T03 | sensor | 0.01 kWh | `_energy_stored` | 1023 changes | |
| Energy stored (max) | T03 | sensor | 0.01 kWh | `_energy_stored_max` | 455 changes (since 2026-03-23) | |
| Energy stored (min) | T02 | sensor | 0.01 kWh | `_energy_stored_min` | 816 changes (since 2026-03-23) | |
| Lift | T02, T04 | sensor | 0.5°C (round 0.1) | `_lift` | 1122 changes (since 2026-03-23) | |
| Power | — | sensor | 0.1 W | `_power_meter` | 11 changes (since 2026-03-24) | |
| Precise temperature | T02, T03 | sensor | 0.25°C (round 0.1) | `_precise_temp` | 744 changes (since 2026-03-23) | |
| Solar temperature | T06 | sensor | 0.5°C | `_T06` | constant: 20.0 (73 entries since 2026-01-10) | |
| Suction temperature | T05 | sensor | 0.5°C | `_T05` | 23135 changes | |
| Superheat | T05, T04 | sensor | 0.5°C (round 0.1) | `_superheat` | 840 changes (since 2026-03-23) | |
| Temperature difference | T02, T01 | sensor | 0.5°C (round 0.1) | `_temp_difference` | 1288 changes | |
| Top temperature | T03 | sensor | 0.5°C | `_T03` | 26609 changes | |

---

## Configuration

All entities in this section are disabled by default. All number entities have step=1.

| Name | Code(s) | Platform | Unit | Range | Precision | History | Status |
|---|---|---|---|---|---|---|---|
| Ambient temp booster no delay | R09 | number | °C | 0–30 | 1 | constant: 5.0 (39 entries since 2026-01-10) | disabled |
| Ambient temp booster with delay | R10 | number | °C | 10–40 | 1 | constant: 25.0 (39 entries since 2026-01-10) | disabled |
| Ambient temp to replace HP | R08 | number | °C | -20–10 | 1 | constant: -5.0 (39 entries since 2026-01-10) | disabled |
| Booster replaces HP | R07 | number | — | 0–1 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Booster setpoint | R05 | number | °C | 30–90 | 1 | constant: 55.0 (39 entries since 2026-01-10) | disabled |
| Booster startup delay | R06 | number | min | 0–90 | 1 | constant: 200.0 (39 entries since 2026-01-10) | disabled |
| Cloud submit interval | H32 | number | min | 1–255 | 1 | constant: 5.0 (39 entries since 2026-01-10) | disabled |
| Compressor shutdown temp | R12 | number | °C | -30–-5 | 1 | constant: -15.0 (39 entries since 2026-01-10) | disabled |
| Compressor stop setpoint 1 | R19 | number | °C | 30–90 | 1 | constant: 65.0 (39 entries since 2026-01-10) | disabled |
| Compressor stop setpoint 2 | R20 | number | °C | 30–90 | 1 | constant: 55.0 (39 entries since 2026-01-10) | disabled |
| Configuration flags | F03 | number | — | — | 1 | constant: 1.0 (39 entries since 2026-01-10) | disabled |
| Defrost duration | D03 | number | min | 30–90 | 1 | constant: 45.0 (39 entries since 2026-01-10) | disabled |
| Defrost duration setting | D11 | number | min | 5–30 | 1 | constant: 10.0 (39 entries since 2026-01-10) | disabled |
| Defrost end temp | D02 | number | °C | 0–30 | 1 | constant: 13.0 (39 entries since 2026-01-10) | disabled |
| Defrost mode | D06 | number | — | 0–2 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Defrost start temp | D01 | number | °C | -30–0 | 1 | constant: -7.0 (39 entries since 2026-01-10) | disabled |
| Delay timer | C01 | number | min | 0–120 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Device address | H30 | number | — | 1–255 | 1 | constant: 1.0 (39 entries since 2026-01-10) | disabled |
| Disinfection duration | G02 | number | min | 0–90 | 1 | constant: 50.0 (39 entries since 2026-01-10) | disabled |
| Disinfection interval | G04 | number | days | 1–99 | 1 | constant: 7.0 (39 entries since 2026-01-10) | disabled |
| Disinfection start time | G03 | time | — | hour only | 1h | constant: 00:00:00 (1 entry since 2026-03-24) | disabled |
| Disinfection target temp | G01 | number | °C | 30–70 | 1 | constant: 60.0 (39 entries since 2026-01-10) | disabled |
| EEV adjustment mode | E01 | number | — | 0–1 | 1 | constant: 1.0 (39 entries since 2026-01-10) | disabled |
| EEV defrost position | E05 | number | — | 0–500 | 1 | constant: 480.0 (39 entries since 2026-01-10) | disabled |
| EEV min opening | E04 | number | — | 0–500 | 1 | constant: 100.0 (39 entries since 2026-01-10) | disabled |
| EEV original position | E03 | number | — | 0–500 | 1 | constant: 240.0 (39 entries since 2026-01-10) | disabled |
| EEV timer setting | E06 | number | — | 0–480 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Enable flag M07 | M07 | number | — | 0–1 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Enable R05 as booster setpoint | R04 | number | — | 0–1 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Energy stored threshold | — | number | kWh | 1–10 | 1 | 2 changes (1→2, since 2026-03-23) | disabled |
| Fan max temp | F07 | number | °C | 0–50 | 1 | constant: 35.0 (39 entries since 2026-01-10) | disabled |
| Fan mode | F01 | number | — | 0–4 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Fan start temp | F06 | number | °C | 0–50 | 1 | constant: 15.0 (39 entries since 2026-01-10) | disabled |
| Frequency setting | F05 | number | Hz | 0–1500 | 1 | constant: 300.0 (39 entries since 2026-01-10) | disabled |
| Frequency step F09 | F09 | number | Hz | 0–1500 | 1 | constant: 320.0 (39 entries since 2026-01-10) | disabled |
| Frequency step F10 | F10 | number | Hz | 0–1500 | 1 | constant: 380.0 (39 entries since 2026-01-10) | disabled |
| Frequency step F11 | F11 | number | Hz | 0–1500 | 1 | constant: 560.0 (39 entries since 2026-01-10) | disabled |
| Frequency step F12 | F12 | number | Hz | 0–1500 | 1 | constant: 700.0 (39 entries since 2026-01-10) | disabled |
| Frequency step F13 | F13 | number | Hz | 0–1500 | 1 | constant: 830.0 (39 entries since 2026-01-10) | disabled |
| HP startup hysteresis (bottom) | R03 | number | °C | 1–20 | 1 | constant: 5.0 (39 entries since 2026-01-10) | disabled |
| HP startup hysteresis (top) | R18 | number | °C | 1–20 | 1 | constant: 3.0 (39 entries since 2026-01-10) | disabled |
| Heater option | H09 | number | — | 0–1 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Heater power level | H16 | number | — | 0–10 | 1 | constant: 6.0 (39 entries since 2026-01-10) | disabled |
| Heating source | H03 | number | — | 0–0 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Intelligent control mode | H31 | number | — | 0–1 | 1 | constant: 1.0 (39 entries since 2026-01-10) | disabled |
| Intelligent defrost judgement | D07 | number | °C | -10–20 | 1 | constant: 2.0 (39 entries since 2026-01-10) | disabled |
| Low temp threshold | D10 | number | °C | -30–5 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Max ambient temp for compressor | R15 | number | °C | 55–80 | 1 | constant: 78.0 (39 entries since 2026-01-10) | disabled |
| Max cycle time | C03 | number | min | 30–120 | 1 | constant: 90.0 (39 entries since 2026-01-10) | disabled |
| Max defrost duration | D04 | number | min | 1–20 | 1 | constant: 4.0 (39 entries since 2026-01-10) | disabled |
| Max frequency | F04 | number | Hz | 0–1500 | 1 | constant: 830.0 (39 entries since 2026-01-10) | disabled |
| Min cycle time | C02 | number | min | 20–60 | 1 | constant: 30.0 (39 entries since 2026-01-10) | disabled |
| Min defrost duration | D05 | number | min | 0–4 | 1 | constant: 44.0 (39 entries since 2026-01-10) | disabled |
| Min frequency | F02 | number | Hz | 0–1500 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Min operating temp | D13 | number | °C | -30–0 | 1 | constant: -18.0 (39 entries since 2026-01-10) | disabled |
| Mode setting R16 | R16 | number | — | 0–3 | 1 | constant: 3.0 (39 entries since 2026-01-10) | disabled |
| Mode/level setting R13 | R13 | number | — | 0–5 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Night decrease end | N06 | time | — | hour only | 1h | constant: 06:00:00 (1 entry since 2026-03-24) | disabled |
| Night decrease start | N05 | time | — | hour only | 1h | constant: 00:00:00 (1 entry since 2026-03-24) | disabled |
| Nighttime temp decrease mode | N04 | number | — | 0–1 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Option flag R11 | R11 | number | — | 0–1 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Precise temperature threshold | — | number | °C | 1–10 | 1 | 2 changes (2→4, since 2026-03-23) | disabled |
| Remember status on power down | H01 | number | — | 0–1 | 1 | constant: 1.0 (39 entries since 2026-01-10) | disabled |
| Run time counter | C05 | number | — | 0–65535 | 1 | constant: 2073.0 (39 entries since 2026-01-10) | disabled |
| Schedule flags | L28 | number | — | — | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Second heat source target | R14 | number | °C | 38–78 | 1 | constant: 45.0 (39 entries since 2026-01-10) | disabled |
| Shown temp compensation | H99 | number | — | 0–1 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Solar pump max runtime | N02 | number | min | 1–30 | 1 | constant: 15.0 (39 entries since 2026-01-10) | disabled |
| Solar pump shutdown temp | N10 | number | °C | 50–90 | 1 | constant: 50.0 (39 entries since 2026-01-10) | disabled |
| Solar pump temp hysteresis | N03 | number | °C | 0–20 | 1 | constant: 20.0 (39 entries since 2026-01-10) | disabled |
| Solar pump working mode | N11 | number | — | 0–1 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Solar temp decrease hysteresis | N08 | number | °C | 1–40 | 1 | constant: 10.0 (39 entries since 2026-01-10) | disabled |
| Solar temp decrease start | N07 | number | °C | 40–90 | 1 | constant: 70.0 (39 entries since 2026-01-10) | disabled |
| Solar water pump sensor | N01 | number | — | 0–1 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Solar water release temp | N09 | number | °C | 50–90 | 1 | constant: 68.0 (39 entries since 2026-01-10) | disabled |
| Sub-mode setting | R02 | number | — | 0–3 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Target superheat | E02 | number | °C | -20–20 | 1 | constant: 7.0 (39 entries since 2026-01-10) | disabled |
| Target temp range | H98 | number | — | 2–3 | 1 | constant: 2.0 (39 entries since 2026-01-10) | disabled |
| Temp differential | D12 | number | °C | 0–20 | 1 | constant: 10.0 (39 entries since 2026-01-10) | disabled |
| Temperature unit | H07 | number | — | 0–1 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Timer 1 end | L08, L09 | time | — | h + min | 1 min | constant: 00:00:00 (1 entry since 2026-03-24) | disabled |
| Timer 1 start | L06, L07 | time | — | h + min | 1 min | constant: 00:00:00 (1 entry since 2026-03-24) | disabled |
| Timer 2 end | L12, L13 | time | — | h + min | 1 min | constant: 00:00:00 (1 entry since 2026-03-24) | disabled |
| Timer 2 start | L10, L11 | time | — | h + min | 1 min | constant: 00:00:00 (1 entry since 2026-03-24) | disabled |
| Timer config | L29 | number | — | 0–255 | 1 | constant: 1.0 (39 entries since 2026-01-10) | disabled |
| Timer date | L02, L03, L04 | date | — | year/month/day | 1 day | constant: 2021-01-01 (1 entry since 2026-03-24) | disabled |
| Timer setting C06 | C06 | number | min | 0–120 | 1 | constant: 52.0 (39 entries since 2026-01-10) | disabled |
| Timer setting C07 | C07 | number | min | 0–120 | 1 | constant: 50.0 (39 entries since 2026-01-10) | disabled |
| Timer setting C08 | C08 | number | min | 0–120 | 1 | constant: 60.0 (39 entries since 2026-01-10) | disabled |
| Timer setting C09 | C09 | number | min | 0–120 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Top sensor controls compressor | R17 | number | — | 0–1 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Usage of OUT 05 | /01 | number | — | 0–2 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |
| Usage of OUT 06 | /02 | number | — | 0–3 | 1 | constant: 0.0 (39 entries since 2026-01-10) | disabled |

---

## Diagnostic

| Name | Code | Platform | Unit / Class | Precision | unique_id suffix | History | Status |
|---|---|---|---|---|---|---|---|
| 3V_DE status | O10 | binary_sensor | — | on/off | `_O10` | constant: off (39 entries since 2026-01-10) | removed |
| 4-way valve | O03 | binary_sensor | — | on/off | `_O03` | constant: off (39 entries since 2026-01-10) | removed |
| Booster runtime | O09 | sensor | h | 1h | `_O09` | constant: 0.0 (73 entries since 2026-01-10) | |
| Compressor | O01 | binary_sensor | running | on/off | `_O01` | constant: off (39 entries since 2026-01-10) | removed |
| Compressor runtime | O08 | sensor | h | 1h | `_O08` | 855 changes | disabled |
| Compressor temperature | T09 | sensor | °C | 1°C | `_T09` | 4071 changes | disabled |
| DTU/WiFi online status | O13 | binary_sensor | connectivity | on/off | `_O13` | constant: off (39 entries since 2026-01-10) | removed |
| Defrost status | O14 | binary_sensor | running | on/off | `_O14` | constant: off (39 entries since 2026-01-10) | removed |
| Device time | M12–M16 | datetime | — | 1 min | `_device_datetime` | 320 changes (since 2026-03-24) | disabled |
| EEPROM storage count | T12 | sensor | — | 1 | `_T12` | constant: unavailable/unknown (4 entries since 2026-01-10) | removed |
| EEV current position | O07 | sensor | — | 2 | `_O07` | 13740 changes | disabled |
| Electrical heater | O02 | binary_sensor | running | on/off | `_O02` | constant: off (39 entries since 2026-01-10) | removed |
| Fan RPM | O29 | sensor | RPM | 10 | `_O29` | 36438 changes | disabled |
| Fan high speed | O04 | binary_sensor | running | on/off | `_O04` | constant: off (39 entries since 2026-01-10) | removed |
| Fan low speed | O05 | binary_sensor | running | on/off | `_O05` | constant: off (39 entries since 2026-01-10) | removed |
| High temp hot water stage | O15 | binary_sensor | — | on/off | `_O15` | constant: off (39 entries since 2026-01-10) | removed |
| MV_DE status | O11 | binary_sensor | — | on/off | `_O11` | constant: off (39 entries since 2026-01-10) | removed |
| Protection count | T11 | sensor | — | 1 | `_T11` | constant: unavailable/unknown (4 entries since 2026-01-10) | removed |
| Run time counter | C05 | sensor | — | 1 | `_C05` | constant: 2073.0 (73 entries since 2026-01-10) | removed |
| Sensor status flags | T08 | sensor | — | 1 | `_T08` | 120 changes | disabled |
| Shutdown status | O12 | binary_sensor | — | on/off | `_O12` | constant: off (39 entries since 2026-01-10) | removed |
| Solar pump/valve | O06 | binary_sensor | running | on/off | `_O06` | constant: off (39 entries since 2026-01-10) | removed |
| Status O18 | O18 | sensor | — | 1 | `_O18` | constant: 0.0 (73 entries since 2026-01-10) | removed |
| Status O19 | O19 | sensor | — | 1 | `_O19` | constant: 0.0 (73 entries since 2026-01-10) | removed |
| Status O20 | O20 | sensor | — | 1 | `_O20` | constant: 0.0 (73 entries since 2026-01-10) | removed |
| Status O21 | O21 | sensor | °C | 1°C | `_O21` | constant: -55.0 (73 entries since 2026-01-10) | removed |
| Status O22 | O22 | sensor | — | 1 | `_O22` | constant: 0.0 (73 entries since 2026-01-10) | removed |
| Status O23 | O23 | sensor | — | 1 | `_O23` | constant: 0.0 (73 entries since 2026-01-10) | removed |
| Status O24 | O24 | sensor | — | 1 | `_O24` | constant: 0.0 (73 entries since 2026-01-10) | removed |
| Status O25 | O25 | sensor | — | 1 | `_O25` | constant: 0.0 (73 entries since 2026-01-10) | removed |
| Status O26 | O26 | sensor | — | 1 | `_O26` | constant: 0.0 (73 entries since 2026-01-10) | removed |
| Status O27 | O27 | sensor | — | 1 | `_O27` | constant: 0.0 (73 entries since 2026-01-10) | removed |
| Status O28 | O28 | sensor | — | 1 | `_O28` | 8542 changes | disabled |
| Status T20 | T20 | sensor | — | 1 | `_T20` | constant: 0.0 (39 entries since 2026-01-10) | removed |
| Status T21 | T21 | sensor | — | 1 | `_T21` | constant: 0.0 (39 entries since 2026-01-10) | removed |
| Status L31 | L31 | sensor | — | 1 | `_L31` | 287 changes | disabled |
| Status L32 | L32 | sensor | — | 1 | `_L32` | 288 changes | disabled |
| Timer status | L30 | sensor | — | 1 | `_L30` | constant: 0.0 (73 entries since 2026-01-10) | removed |
| WiFi signal | — | sensor | % | 1% | `_wifi_signal` | 43 changes | disabled |
