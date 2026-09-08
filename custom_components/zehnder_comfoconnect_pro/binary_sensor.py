"""Binary status entities for documented discrete inputs and coils."""

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COILS, DISCRETE_INPUTS


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        ComfoBinary(entry.runtime_data, entry, key, definition)
        for key, definition in (DISCRETE_INPUTS | COILS).items()
    )


class ComfoBinary(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry, key, definition):
        super().__init__(coordinator)
        address, device_class, icon = definition
        self.key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self.entity_description = BinarySensorEntityDescription(
            key=key, translation_key=key, device_class=device_class, icon=icon
        )
        self._attr_extra_state_attributes = {
            "register": address,
            "register_type": "discrete_input" if key in DISCRETE_INPUTS else "coil",
            "read_only": key in DISCRETE_INPUTS,
        }

    @property
    def is_on(self):
        return self.coordinator.data.get(self.key)
