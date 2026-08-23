from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import PROFILE_NAMES


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([ComfoProfile(entry.runtime_data, entry)])


class ComfoProfile(CoordinatorEntity, SelectEntity):
    _attr_options = list(PROFILE_NAMES.values())
    _attr_translation_key = "temperature_profile"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_temperature_profile"

    @property
    def current_option(self):
        return PROFILE_NAMES.get(self.coordinator.data.get("temperature_profile"))

    async def async_select_option(self, option):
        await self.coordinator.write_profile(
            next(key for key, value in PROFILE_NAMES.items() if value == option)
        )
