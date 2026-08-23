from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import HOLDING_REGISTERS, INPUT_REGISTERS


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        ComfoSensor(entry.runtime_data, entry, key, definition)
        for key, definition in INPUT_REGISTERS.items() | HOLDING_REGISTERS.items()
    )


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
