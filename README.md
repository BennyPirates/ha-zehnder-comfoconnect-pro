# Zehnder ComfoConnect Pro
Local HACS integration for the Zehnder ComfoConnect Pro Modbus TCP interface.

It replaces the supplied YAML Modbus, template, switch, and fan definitions with native entities: air sensors, Away/Boost binary sensors, a ventilation fan, a temperature-profile select, and Away/Low/Normal/High/Boost buttons. The fan preserves your controls: 0% Away, 1–33% Low, 34–66% Normal, 67–99% High, and 100% Boost (600 seconds).

The integration writes only holding registers 0 (level), 1 (temperature profile), and 4 (boost duration). Keep the old package enabled while values and controls are checked; update scripts/automations to use the native fan/select entities before removing it.

Transient Modbus TCP failures are retried once with a fresh socket. This allows the
integration to recover automatically after the ComfoConnect gateway is power-cycled.
