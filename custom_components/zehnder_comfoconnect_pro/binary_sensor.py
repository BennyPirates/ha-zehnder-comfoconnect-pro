from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        [
            ComfoBinary(entry.runtime_data, entry, "boost_active", "running"),
            ComfoBinary(entry.runtime_data, entry, "away_active", "occupancy"),
        ]
    )


class ComfoBinary(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry, key, device_class):
        super().__init__(coordinator)
        self.key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self.entity_description = BinarySensorEntityDescription(
            key=key, translation_key=key, device_class=device_class
        )

    @property
    def is_on(self):
        data = self.coordinator.data
        return (
            data.get("ventilation_level") == 3
            and data.get("remaining_boost_time", 0) > 0
            if self.key == "boost_active"
            else data.get("ventilation_level") == 0
        )
