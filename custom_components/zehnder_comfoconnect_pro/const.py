"""Constants and documented local Modbus map."""

DOMAIN = "zehnder_comfoconnect_pro"
PLATFORMS = ["sensor", "binary_sensor", "fan", "select", "button"]
DEFAULT_PORT = 502
DEFAULT_UNIT_ID = 1
DEFAULT_SCAN_INTERVAL = 10
CONF_UNIT_ID = "unit_id"

# Zero-based PDU addresses; Zehnder's published register numbers are one-based.
# Tuple: address, scale, unit, device class, signed value.
INPUT_REGISTERS = {
    "connection_state": (0, 1, None, None, False),
    "active_error_1": (1, 1, None, None, False),
    "active_error_2": (2, 1, None, None, False),
    "active_error_3": (3, 1, None, None, False),
    "active_error_4": (4, 1, None, None, False),
    "active_error_5": (5, 1, None, None, False),
    "air_volume": (6, 1, "m³/h", None, False),
    "room_air_temperature": (7, 0.1, "°C", "temperature", True),
    "extract_air_temperature": (8, 0.1, "°C", "temperature", True),
    "exhaust_air_temperature": (9, 0.1, "°C", "temperature", True),
    "outdoor_air_temperature": (10, 0.1, "°C", "temperature", True),
    "supply_air_temperature": (11, 0.1, "°C", "temperature", True),
    "room_air_humidity": (12, 1, "%", "humidity", False),
    "extract_air_humidity": (13, 1, "%", "humidity", False),
    "exhaust_air_humidity": (14, 1, "%", "humidity", False),
    "outdoor_air_humidity": (15, 1, "%", "humidity", False),
    "supply_air_humidity": (16, 1, "%", "humidity", False),
    "co2_zone_1": (17, 1, "ppm", "carbon_dioxide", False),
    "co2_zone_2": (18, 1, "ppm", "carbon_dioxide", False),
    "co2_zone_3": (19, 1, "ppm", "carbon_dioxide", False),
    "co2_zone_4": (20, 1, "ppm", "carbon_dioxide", False),
    "co2_zone_5": (21, 1, "ppm", "carbon_dioxide", False),
    "co2_zone_6": (22, 1, "ppm", "carbon_dioxide", False),
    "co2_zone_7": (23, 1, "ppm", "carbon_dioxide", False),
    "co2_zone_8": (24, 1, "ppm", "carbon_dioxide", False),
    "filter_days_remaining": (25, 1, "d", "duration", False),
}

HOLDING_REGISTERS = {
    "ventilation_level": (0, 1, None, None, False),
    "temperature_profile": (1, 1, None, None, False),
    "temperature_profile_mode": (2, 1, None, None, False),
    "comfort_temperature_setpoint": (3, 0.1, "°C", "temperature", False),
    # Legacy key/unique ID retained. This is the configured party-timer duration.
    "remaining_boost_time": (4, 1, "s", "duration", False),
}

DISCRETE_INPUTS = {
    "error_active": (0, "problem", "mdi:alert-circle"),
    "standby_active": (1, None, "mdi:power-sleep"),
    "comfohood_active": (2, None, "mdi:stove"),
    "filter_replacement_required": (3, "problem", "mdi:air-filter"),
}

# Coil zero is a self-resetting fault acknowledgement command, exposed as a button.
COILS = {
    "preset_away_active": (1, None, "mdi:home-export-outline"),
    "preset_1_active": (2, None, "mdi:fan-speed-1"),
    "preset_2_active": (3, None, "mdi:fan-speed-2"),
    "preset_3_active": (4, None, "mdi:fan-speed-3"),
    "auto_mode_active": (5, None, "mdi:fan-auto"),
    "boost_active": (6, "running", "mdi:fan-plus"),
    "away_active": (7, "occupancy", "mdi:home-export-outline"),
    "comfocool_active": (8, "running", "mdi:snowflake"),
}

PROFILE_NAMES = {0: "Normal", 1: "Cool", 2: "Warm"}
PROFILE_MODE_NAMES = {0: "Adaptive", 1: "Fixed", 2: "External setpoint"}
CONNECTION_STATE_NAMES = {
    0: "Connected",
    30: "Wrong ventilation unit",
    40: "Incompatible ventilation unit version",
    50: "No ventilation unit detected",
}

ERROR_NAMES = {
    0: "No error",
    21: "Temperature sensors out of range",
    22: "Ventilation unit temperature too high",
    23: "Temperature sensor T11 exceeded limit too often",
    24: "Temperature sensor T11 outside limit",
    25: "Temperature sensor T12 exceeded limit too often",
    26: "Temperature sensor T12 outside limit",
    27: "Temperature sensor T20 exceeded limit too often",
    28: "Temperature sensor T20 outside limit",
    29: "Temperature sensor T21 exceeded limit too often",
    30: "Temperature sensor T21 outside limit",
    31: "Temperature sensor T22 exceeded limit too often",
    32: "Temperature sensor T22 outside limit",
    33: "Ventilation unit not initialized",
    34: "Front door open",
    35: "Preheater position mismatch",
    37: "Preheater insufficient power",
    38: "Preheater power ratio insufficient",
    39: "Humidity sensor 11 exceeded limit too often",
    41: "Humidity sensor 12 exceeded limit too often",
    43: "Humidity sensor 20 exceeded limit too often",
    45: "Humidity sensor 21 exceeded limit too often",
    47: "Humidity sensor 22 exceeded limit too often",
    49: "Pressure sensor P12 exceeded limit too often",
    50: "Pressure sensor P22 exceeded limit too often",
    51: "Fan F12 speed exceeded limit too often",
    52: "Fan F22 speed exceeded limit too often",
    53: "Static pressure P12 exceeded limit too often",
    54: "Static pressure P22 exceeded limit too often",
    55: "Required fan F12 speed not reached",
    56: "Required fan F22 speed not reached",
    57: "Required fan F12 airflow not reached",
    58: "Required fan F22 airflow not reached",
    59: "Required outdoor-air temperature not reached",
    60: "Required supply-air temperature not reached",
    61: "Supply-air temperature too low",
    62: "Airflow imbalance outside tolerance",
    66: "RF hardware no longer detected",
    67: "Option board no longer detected",
    68: "Preheater no longer detected",
    69: "Post-heater no longer detected",
    74: "Cooker hood no longer detected",
    75: "ComfoCool no longer detected",
    76: "ComfoFond no longer detected",
    77: "Replace filters now",
    78: "External filter input active",
    79: "Order replacement filters",
    80: "Standby active",
    81: "Preheater communication unreliable",
    89: "Bypass in manual mode",
    90: "ComfoCool overheated",
    91: "ComfoCool compressor error",
    92: "ComfoCool room temperature out of range",
    93: "ComfoCool compressor temperature out of range",
    94: "ComfoCool supply temperature out of range",
    95: "Cooker hood temperature too high",
    96: "Cooker hood active",
    97: "Minimum airflow constraint active",
    98: "Preheater current too low",
    99: "Configuration error",
    100: "Analysis in progress",
    101: "ComfoNet bus error",
    102: "CO₂ sensor count decreased",
    103: "Too many CO₂ sensors",
    104: "CO₂ sensor error",
}
