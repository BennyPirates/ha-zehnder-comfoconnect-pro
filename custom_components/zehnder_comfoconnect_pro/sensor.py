from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import HOLDING_REGISTERS, INPUT_REGISTERS


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
        address, _, unit, device_class = definition
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
        return self.coordinator.data.get(self.key)


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
        boost_time = self.coordinator.data.get("remaining_boost_time", 0)
        modes = {0: "Away", 1: "Low", 2: "Normal"}

        if level == 3:
            return "Boost" if boost_time > 0 else "High"

        return modes.get(level, "Unknown")
