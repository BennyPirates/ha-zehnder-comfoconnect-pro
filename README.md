# Zehnder ComfoConnect Pro
Local HACS integration for the Zehnder ComfoConnect Pro Modbus TCP interface.

It replaces the supplied YAML Modbus, template, switch, and fan definitions with native entities for the complete documented register map: connection and error states, room and duct air sensors, eight CO₂ zones, filter lifetime and replacement status, ventilation/coil states, configuration values, a ventilation fan, a temperature-profile select, preset buttons, and an error-acknowledgement button. The fan maps 0% to Away, 1–33% to Low, 34–66% to Normal, 67–99% to High, and 100% to a 600-second Boost.

The integration writes only documented controls: holding registers 0 (level), 1 (temperature profile), and 4 (party-timer duration), plus coils 0 (acknowledge errors) and 6 (activate Boost). All documented values are read in four contiguous Modbus requests per update rather than one request per entity.

Transient Modbus TCP failures are retried once with a fresh socket. This allows the
integration to recover automatically after the ComfoConnect gateway is power-cycled.
