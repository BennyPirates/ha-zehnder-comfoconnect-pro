from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import (
    CONNECTION_STATE_NAMES,
    ERROR_NAMES,
    HOLDING_REGISTERS,
    INPUT_REGISTERS,
    PROFILE_MODE_NAMES,
)


async def async_setup_entry(hass, entry, async_add_entities):
    entities = [
        ComfoSensor(entry.runtime_data, entry, key, definition)
        for key, definition in INPUT_REGISTERS.items() | HOLDING_REGISTERS.items()
    ]
    entities.append(ComfoVentilationModeSensor(entry.runtime_data, entry))
    async_add_entities(entities)


class ComfoSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, key, definition):
        super().__init__(coordinator)
        address, _, unit, device_class, _ = definition
        self.key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self.entity_description = SensorEntityDescription(
            key=key,
            translation_key=key,
            native_unit_of_measurement=unit,
            device_class=device_class,
        )
        self._attr_extra_state_attributes = {"register": address, "read_only": True}

    @property
    def native_value(self):
        value = self.coordinator.data.get(self.key)
        if value is None:
            return None
        if self.key == "connection_state":
            return CONNECTION_STATE_NAMES.get(value, f"Unknown state ({value})")
        if self.key.startswith("active_error_"):
            return ERROR_NAMES.get(value, f"Unknown error ({value})")
        if self.key == "temperature_profile_mode":
            return PROFILE_MODE_NAMES.get(value, f"Unknown mode ({value})")
        return value


class ComfoVentilationModeSensor(CoordinatorEntity, SensorEntity):
    """Expose the operating mode derived from the device's level and boost timer."""

    _attr_translation_key = "ventilation_mode"
    _attr_icon = "mdi:fan"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_ventilation_mode"

    @property
    def native_value(self):
        level = self.coordinator.data.get("ventilation_level")
        boost_active = self.coordinator.data.get("boost_active", False)
        modes = {0: "Away", 1: "Low", 2: "Normal"}

        if level == 3:
            return "Boost" if boost_active else "High"

        return modes.get(level, "Unknown")
