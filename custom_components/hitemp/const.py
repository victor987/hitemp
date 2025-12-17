"""Constants for the HiTemp integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

DOMAIN: Final = "hitemp"

# API Configuration
BASE_URL: Final = "https://cloud.linked-go.com:449/crmservice/api"
API_LOGIN: Final = "/app/user/login"
API_DEVICE_LIST: Final = "/app/device/getMyAppectDeviceShareDataList"
API_GET_DATA: Final = "/app/device/getDataByCode"
API_CONTROL: Final = "/app/device/control"

# Product ID for HiTemp devices
PRODUCT_ID: Final = "1245226668902080512"

# Update interval in seconds
UPDATE_INTERVAL: Final = 30

# Mode mappings: mode_real value -> preset name
MODE_TO_PRESET: Final = {
    0: "intelligent",
    2: "eco",
    3: "hybrid",
    4: "fast",
}

PRESET_TO_MODE: Final = {v: k for k, v in MODE_TO_PRESET.items()}

# Temperature limits for climate entity
MIN_TEMP: Final = 38
MAX_TEMP: Final = 75


@dataclass(frozen=True)
class ParamDef:
    """Parameter definition with metadata."""

    code: str
    name: str
    unit: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    writable: bool = False
    category: str = "other"


# =============================================================================
# SPECIAL CONTROL PARAMETERS
# =============================================================================
PARAMS_CONTROL: Final = {
    "Power": ParamDef("Power", "Power", None, 0, 1, True, "control"),
    "mode_real": ParamDef("mode_real", "Operating mode", None, 0, 4, True, "control"),
    "Mode": ParamDef("Mode", "Operating mode (mirror)", None, 0, 7, True, "control"),
}

# =============================================================================
# OUTPUT CONFIGURATION (/ codes)
# =============================================================================
PARAMS_OUTPUT: Final = {
    "/01": ParamDef("/01", "Usage of OUT 05", None, 0, 2, True, "output"),
    "/02": ParamDef("/02", "Usage of OUT 06", None, 0, 3, True, "output"),
}

# =============================================================================
# C CODES - COMPRESSOR/CYCLE SETTINGS
# =============================================================================
PARAMS_COMPRESSOR: Final = {
    "C01": ParamDef("C01", "Delay timer", "min", 0, 120, True, "compressor"),
    "C02": ParamDef("C02", "Min cycle time", "min", 20, 60, True, "compressor"),
    "C03": ParamDef("C03", "Max cycle time", "min", 30, 120, True, "compressor"),
    "C05": ParamDef("C05", "Run time counter", None, 0, 65535, True, "compressor"),
    "C06": ParamDef("C06", "Timer setting C06", "min", 0, 120, True, "compressor"),
    "C07": ParamDef("C07", "Timer setting C07", "min", 0, 120, True, "compressor"),
    "C08": ParamDef("C08", "Timer setting C08", "min", 0, 120, True, "compressor"),
    "C09": ParamDef("C09", "Timer setting C09", "min", 0, 120, True, "compressor"),
}

# =============================================================================
# D CODES - DEFROST SETTINGS
# =============================================================================
PARAMS_DEFROST: Final = {
    "D01": ParamDef("D01", "Defrost start temp", "°C", -30, 0, True, "defrost"),
    "D02": ParamDef("D02", "Defrost end temp", "°C", 0, 30, True, "defrost"),
    "D03": ParamDef("D03", "Defrost duration", "min", 30, 90, True, "defrost"),
    "D04": ParamDef("D04", "Max defrost duration", "min", 1, 20, True, "defrost"),
    "D05": ParamDef("D05", "Min defrost duration", "min", 0, 4, True, "defrost"),
    "D06": ParamDef("D06", "Defrost mode", None, 0, 2, True, "defrost"),
    "D07": ParamDef("D07", "Intelligent defrost judgement", "°C", -10, 20, True, "defrost"),
    "D10": ParamDef("D10", "Low temp threshold", "°C", -30, 5, True, "defrost"),
    "D11": ParamDef("D11", "Defrost duration setting", "min", 5, 30, True, "defrost"),
    "D12": ParamDef("D12", "Temp differential", "°C", 0, 20, True, "defrost"),
    "D13": ParamDef("D13", "Min operating temp", "°C", -30, 0, True, "defrost"),
}

# =============================================================================
# E CODES - ELECTRONIC EXPANSION VALVE SETTINGS
# =============================================================================
PARAMS_EEV: Final = {
    "E01": ParamDef("E01", "EEV adjustment mode", None, 0, 1, True, "eev"),
    "E02": ParamDef("E02", "Target superheat", "°C", -20, 20, True, "eev"),
    "E03": ParamDef("E03", "EEV original position", None, 0, 500, True, "eev"),
    "E04": ParamDef("E04", "EEV min opening", None, 0, 500, True, "eev"),
    "E05": ParamDef("E05", "EEV defrost position", None, 0, 500, True, "eev"),
    "E06": ParamDef("E06", "EEV timer setting", None, 0, 480, True, "eev"),
}

# =============================================================================
# F CODES - FAN/FREQUENCY SETTINGS
# =============================================================================
PARAMS_FAN: Final = {
    "F01": ParamDef("F01", "Fan mode", None, 0, 4, True, "fan"),
    "F02": ParamDef("F02", "Min frequency", "Hz", 0, 1500, True, "fan"),
    "F03": ParamDef("F03", "Configuration flags", None, None, None, True, "fan"),
    "F04": ParamDef("F04", "Max frequency", "Hz", 0, 1500, True, "fan"),
    "F05": ParamDef("F05", "Frequency setting", "Hz", 0, 1500, True, "fan"),
    "F06": ParamDef("F06", "Fan start temp", "°C", 0, 50, True, "fan"),
    "F07": ParamDef("F07", "Fan max temp", "°C", 0, 50, True, "fan"),
    "F09": ParamDef("F09", "Frequency step F09", "Hz", 0, 1500, True, "fan"),
    "F10": ParamDef("F10", "Frequency step F10", "Hz", 0, 1500, True, "fan"),
    "F11": ParamDef("F11", "Frequency step F11", "Hz", 0, 1500, True, "fan"),
    "F12": ParamDef("F12", "Frequency step F12", "Hz", 0, 1500, True, "fan"),
    "F13": ParamDef("F13", "Frequency step F13", "Hz", 0, 1500, True, "fan"),
}

# =============================================================================
# G CODES - DISINFECTION SETTINGS
# =============================================================================
PARAMS_DISINFECTION: Final = {
    "G01": ParamDef("G01", "Disinfection target temp", "°C", 30, 70, True, "disinfection"),
    "G02": ParamDef("G02", "Disinfection duration", "min", 0, 90, True, "disinfection"),
    "G03": ParamDef("G03", "Disinfection start hour", "h", 0, 23, True, "disinfection"),
    "G04": ParamDef("G04", "Disinfection interval", "days", 1, 99, True, "disinfection"),
}

# =============================================================================
# H CODES - HEATER SETTINGS
# =============================================================================
PARAMS_HEATER: Final = {
    "H01": ParamDef("H01", "Remember status on power down", None, 0, 1, True, "heater"),
    "H03": ParamDef("H03", "Heating source", None, 0, 0, True, "heater"),
    "H07": ParamDef("H07", "Temperature unit", None, 0, 1, True, "heater"),
    "H09": ParamDef("H09", "Heater option", None, 0, 1, True, "heater"),
    "H16": ParamDef("H16", "Heater power level", None, 0, 10, True, "heater"),
    "H30": ParamDef("H30", "Device address", None, 1, 255, True, "heater"),
    "H31": ParamDef("H31", "Intelligent control mode", None, 0, 1, True, "heater"),
    "H32": ParamDef("H32", "Cloud submit interval", "min", 1, 255, True, "heater"),
    "H98": ParamDef("H98", "Target temp range", None, 2, 3, True, "heater"),
    "H99": ParamDef("H99", "Shown temp compensation", None, 0, 1, True, "heater"),
}

# =============================================================================
# L CODES - TIMER SCHEDULE
# =============================================================================
PARAMS_TIMER: Final = {
    "L02": ParamDef("L02", "Year (20XX)", "year", 20, 99, True, "timer"),
    "L03": ParamDef("L03", "Month", "month", 1, 12, True, "timer"),
    "L04": ParamDef("L04", "Day", "day", 1, 31, True, "timer"),
    "L06": ParamDef("L06", "Timer 1 start hour", "h", 0, 23, True, "timer"),
    "L07": ParamDef("L07", "Timer 1 start minute", "min", 0, 59, True, "timer"),
    "L08": ParamDef("L08", "Timer 1 end hour", "h", 0, 23, True, "timer"),
    "L09": ParamDef("L09", "Timer 1 end minute", "min", 0, 59, True, "timer"),
    "L10": ParamDef("L10", "Timer 2 start hour", "h", 0, 23, True, "timer"),
    "L11": ParamDef("L11", "Timer 2 start minute", "min", 0, 59, True, "timer"),
    "L12": ParamDef("L12", "Timer 2 end hour", "h", 0, 23, True, "timer"),
    "L13": ParamDef("L13", "Timer 2 end minute", "min", 0, 59, True, "timer"),
    "L28": ParamDef("L28", "Schedule flags", None, None, None, True, "timer"),
    "L29": ParamDef("L29", "Timer config", None, 0, 255, True, "timer"),
    "L30": ParamDef("L30", "Timer status", None, None, None, False, "timer"),
    "L31": ParamDef("L31", "Timer counter L31", None, None, None, False, "timer"),
    "L32": ParamDef("L32", "Timer counter L32", None, None, None, False, "timer"),
}

# =============================================================================
# M CODES - MODE/TIME SETTINGS
# =============================================================================
PARAMS_MODE: Final = {
    "M06": ParamDef("M06", "Mode setting M06", None, 1, 2, True, "mode"),
    "M07": ParamDef("M07", "Enable flag M07", None, 0, 1, True, "mode"),
    "M12": ParamDef("M12", "Device time minute", "min", 0, 59, True, "mode"),
    "M13": ParamDef("M13", "Device time hour", "h", 0, 23, True, "mode"),
    "M14": ParamDef("M14", "Device time day", "day", 1, 31, True, "mode"),
    "M15": ParamDef("M15", "Device time month", "month", 1, 12, True, "mode"),
    "M16": ParamDef("M16", "Device time year", "year", 0, 99, True, "mode"),
    "M17": ParamDef("M17", "Fan status", None, None, None, False, "mode"),
}

# =============================================================================
# N CODES - SOLAR SETTINGS
# =============================================================================
PARAMS_SOLAR: Final = {
    "N01": ParamDef("N01", "Solar water pump sensor", None, 0, 1, True, "solar"),
    "N02": ParamDef("N02", "Solar pump max runtime", "min", 1, 30, True, "solar"),
    "N03": ParamDef("N03", "Solar pump temp hysteresis", "°C", 0, 20, True, "solar"),
    "N04": ParamDef("N04", "Nighttime temp decrease mode", None, 0, 1, True, "solar"),
    "N05": ParamDef("N05", "Night decrease start hour", "h", 0, 23, True, "solar"),
    "N06": ParamDef("N06", "Night decrease end hour", "h", 0, 23, True, "solar"),
    "N07": ParamDef("N07", "Solar temp decrease start", "°C", 40, 90, True, "solar"),
    "N08": ParamDef("N08", "Solar temp decrease hysteresis", "°C", 1, 40, True, "solar"),
    "N09": ParamDef("N09", "Solar water release temp", "°C", 50, 90, True, "solar"),
    "N10": ParamDef("N10", "Solar pump shutdown temp", "°C", 50, 90, True, "solar"),
    "N11": ParamDef("N11", "Solar pump working mode", None, 0, 1, True, "solar"),
}

# =============================================================================
# O CODES - OPERATING DATA (mostly read-only)
# =============================================================================
PARAMS_OPERATING: Final = {
    "O01": ParamDef("O01", "Compressor", None, None, None, False, "operating"),
    "O02": ParamDef("O02", "Electrical heater", None, None, None, False, "operating"),
    "O03": ParamDef("O03", "4-way valve", None, None, None, False, "operating"),
    "O04": ParamDef("O04", "Fan high speed", None, None, None, False, "operating"),
    "O05": ParamDef("O05", "Fan low speed", None, None, None, False, "operating"),
    "O06": ParamDef("O06", "Solar pump/valve", None, None, None, False, "operating"),
    "O07": ParamDef("O07", "EEV current position", None, None, None, False, "operating"),
    "O08": ParamDef("O08", "Compressor runtime", "h", None, None, False, "operating"),
    "O09": ParamDef("O09", "Booster runtime", "h", None, None, False, "operating"),
    "O10": ParamDef("O10", "3V_DE status", None, None, None, False, "operating"),
    "O11": ParamDef("O11", "MV_DE status", None, None, None, False, "operating"),
    "O12": ParamDef("O12", "Shutdown status", None, None, None, False, "operating"),
    "O13": ParamDef("O13", "DTU/WiFi online status", None, None, None, False, "operating"),
    "O14": ParamDef("O14", "Defrost status", None, None, None, False, "operating"),
    "O15": ParamDef("O15", "High temp hot water stage", None, None, None, False, "operating"),
    "O18": ParamDef("O18", "Status O18", None, None, None, False, "operating"),
    "O19": ParamDef("O19", "Status O19", None, None, None, False, "operating"),
    "O20": ParamDef("O20", "Status O20", None, None, None, False, "operating"),
    "O21": ParamDef("O21", "Temp sensor O21", "°C", None, None, False, "operating"),
    "O22": ParamDef("O22", "Status O22", None, None, None, False, "operating"),
    "O23": ParamDef("O23", "Status O23", None, None, None, False, "operating"),
    "O24": ParamDef("O24", "Status O24", None, None, None, False, "operating"),
    "O25": ParamDef("O25", "Status O25", None, None, None, False, "operating"),
    "O26": ParamDef("O26", "Status O26", None, None, None, False, "operating"),
    "O27": ParamDef("O27", "Status O27", None, None, None, False, "operating"),
    "O28": ParamDef("O28", "Status O28", None, None, None, False, "operating"),
    "O29": ParamDef("O29", "Compressor speed", "Hz", None, None, False, "operating"),
}

# =============================================================================
# R CODES - MAIN SETTINGS
# =============================================================================
PARAMS_MAIN: Final = {
    "R01": ParamDef("R01", "Target temperature", "°C", 38, 75, True, "main"),
    "R02": ParamDef("R02", "Sub-mode setting", None, 0, 3, True, "main"),
    "R03": ParamDef("R03", "HP startup hysteresis (bottom)", "°C", 1, 20, True, "main"),
    "R04": ParamDef("R04", "Enable R05 as booster setpoint", None, 0, 1, True, "main"),
    "R05": ParamDef("R05", "Booster setpoint", "°C", 30, 90, True, "main"),
    "R06": ParamDef("R06", "Booster startup delay", "min", 0, 90, True, "main"),
    "R07": ParamDef("R07", "Booster replaces HP", None, 0, 1, True, "main"),
    "R08": ParamDef("R08", "Ambient temp to replace HP", "°C", -20, 10, True, "main"),
    "R09": ParamDef("R09", "Ambient temp booster no delay", "°C", 0, 30, True, "main"),
    "R10": ParamDef("R10", "Ambient temp booster with delay", "°C", 10, 40, True, "main"),
    "R11": ParamDef("R11", "Option flag R11", None, 0, 1, True, "main"),
    "R12": ParamDef("R12", "Compressor shutdown temp", "°C", -30, -5, True, "main"),
    "R13": ParamDef("R13", "Mode/level setting R13", None, 0, 5, True, "main"),
    "R14": ParamDef("R14", "Second heat source target", "°C", 38, 78, True, "main"),
    "R15": ParamDef("R15", "Max ambient temp for compressor", "°C", 55, 80, True, "main"),
    "R16": ParamDef("R16", "Mode setting R16", None, 0, 3, True, "main"),
    "R17": ParamDef("R17", "Top sensor controls compressor", None, 0, 1, True, "main"),
    "R18": ParamDef("R18", "HP startup hysteresis (top)", "°C", 1, 20, True, "main"),
    "R19": ParamDef("R19", "Compressor stop setpoint 1", "°C", 30, 90, True, "main"),
    "R20": ParamDef("R20", "Compressor stop setpoint 2", "°C", 30, 90, True, "main"),
}

# =============================================================================
# T CODES - TEMPERATURE SENSORS
# =============================================================================
PARAMS_TEMP: Final = {
    "T01": ParamDef("T01", "Ambient temperature", "°C", None, None, False, "temp"),
    "T02": ParamDef("T02", "Bottom temperature", "°C", None, None, False, "temp"),
    "T03": ParamDef("T03", "Top temperature", "°C", None, None, False, "temp"),
    "T04": ParamDef("T04", "Coil temperature", "°C", None, None, False, "temp"),
    "T05": ParamDef("T05", "Suction temperature", "°C", None, None, False, "temp"),
    "T06": ParamDef("T06", "Solar temperature", "°C", None, None, False, "temp"),
    "T07": ParamDef("T07", "Discharge temperature", "°C", None, None, False, "temp"),
    "T08": ParamDef("T08", "Sensor status flags", None, None, None, False, "temp"),
    "T09": ParamDef("T09", "Temp sensor T09", None, None, None, False, "temp"),
    "T10": ParamDef("T10", "Display temperature", "°C", None, None, False, "temp"),
    "T11": ParamDef("T11", "Protection count", None, None, None, False, "temp"),
    "T12": ParamDef("T12", "EEPROM storage count", None, None, None, False, "temp"),
    "T20": ParamDef("T20", "Status T20", None, None, None, False, "temp"),
    "T21": ParamDef("T21", "Status T21", None, None, None, False, "temp"),
}

# =============================================================================
# ALL PARAMETERS COMBINED
# =============================================================================
ALL_PARAM_DEFS: Final = {
    **PARAMS_CONTROL,
    **PARAMS_OUTPUT,
    **PARAMS_COMPRESSOR,
    **PARAMS_DEFROST,
    **PARAMS_EEV,
    **PARAMS_FAN,
    **PARAMS_DISINFECTION,
    **PARAMS_HEATER,
    **PARAMS_TIMER,
    **PARAMS_MODE,
    **PARAMS_SOLAR,
    **PARAMS_OPERATING,
    **PARAMS_MAIN,
    **PARAMS_TEMP,
}

# List of all parameter codes to fetch
ALL_PARAMS: Final = list(ALL_PARAM_DEFS.keys())

# Binary status parameters (O codes that are on/off)
BINARY_STATUS_PARAMS: Final = [
    "Power", "O01", "O02", "O03", "O04", "O05", "O06",
    "O10", "O11", "O12", "O13", "O14", "O15",
]

# Temperature sensor parameters
TEMP_SENSOR_PARAMS: Final = ["T01", "T02", "T03", "T04", "T05", "T06", "T07", "T10"]

# Numeric sensor parameters (read-only values that aren't temp or binary)
NUMERIC_SENSOR_PARAMS: Final = [
    "O07", "O08", "O09", "O18", "O19", "O20", "O21", "O22", "O23",
    "O24", "O25", "O26", "O27", "O28", "O29", "C05",
    "L30", "L31", "L32", "T08", "T09", "T11", "T12", "T20", "T21", "M17",
]

# Writable number parameters (settings)
WRITABLE_NUMBER_PARAMS: Final = [
    code for code, param in ALL_PARAM_DEFS.items()
    if param.writable and code not in ["Power", "mode_real", "Mode", "R01"]
]
