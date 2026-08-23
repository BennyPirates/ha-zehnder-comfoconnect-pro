"""Constants and documented local Modbus map."""

DOMAIN = "zehnder_comfoconnect_pro"
PLATFORMS = ["sensor", "binary_sensor", "fan", "select"]
DEFAULT_PORT = 502
DEFAULT_UNIT_ID = 1
DEFAULT_SCAN_INTERVAL = 10
CONF_UNIT_ID = "unit_id"
INPUT_REGISTERS = {
    "extract_air_temperature": (8, 0.1, "°C", "temperature"),
    "extract_air_humidity": (13, 1, "%", "humidity"),
    "exhaust_air_temperature": (9, 0.1, "°C", "temperature"),
    "exhaust_air_humidity": (14, 1, "%", "humidity"),
    "outdoor_air_temperature": (10, 0.1, "°C", "temperature"),
    "outdoor_air_humidity": (15, 1, "%", "humidity"),
    "supply_air_temperature": (11, 0.1, "°C", "temperature"),
    "supply_air_humidity": (16, 1, "%", "humidity"),
    "air_volume": (6, 1, "m³/h", None),
}
HOLDING_REGISTERS = {
    "ventilation_level": (0, 1, None, None),
    "temperature_profile": (1, 1, None, None),
    "comfort_temperature_setpoint": (3, 0.1, "°C", "temperature"),
    "remaining_boost_time": (4, 1, "s", "duration"),
}
PROFILE_NAMES = {0: "Normal", 1: "Cool", 2: "Warm"}
