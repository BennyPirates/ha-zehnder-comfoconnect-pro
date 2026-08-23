from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.helpers.update_coordinator import CoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([ComfoFan(entry.runtime_data, entry)])


class ComfoFan(CoordinatorEntity, FanEntity):
    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_ventilation"
        self._attr_translation_key = "ventilation"

    @property
    def is_on(self):
        return self.coordinator.data.get("ventilation_level", 0) > 0

    @property
    def percentage(self):
        data = self.coordinator.data
        if data.get("remaining_boost_time", 0) > 0:
            return 100
        return min(data.get("ventilation_level", 0) * 33, 99)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.write_level(0)

    async def async_turn_on(self, **kwargs):
        await self.coordinator.write_level(
            max(1, self.coordinator.data.get("ventilation_level", 0))
        )

    async def async_set_percentage(self, percentage):
        level = (
            0
            if percentage == 0
            else 1
            if percentage <= 33
            else 2
            if percentage <= 66
            else 3
        )
        await self.coordinator.write_level(level, boost=percentage == 100)
