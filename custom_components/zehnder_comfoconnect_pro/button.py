"""Native ventilation presets for Zehnder ComfoConnect Pro."""

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

PRESETS: tuple[tuple[str, int, bool, str], ...] = (
    ("set_away", 0, False, "mdi:home-export-outline"),
    ("set_low", 1, False, "mdi:fan-speed-1"),
    ("set_normal", 2, False, "mdi:fan-speed-2"),
    ("set_high", 3, False, "mdi:fan-speed-3"),
    ("set_boost", 3, True, "mdi:fan-plus"),
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up the documented ventilation presets."""
    async_add_entities(
        ComfoPresetButton(entry.runtime_data, entry, key, level, boost, icon)
        for key, level, boost, icon in PRESETS
    )


class ComfoPresetButton(CoordinatorEntity, ButtonEntity):
    """Set a documented ventilation level without requiring a YAML script."""

    def __init__(self, coordinator, entry, key, level, boost, icon) -> None:
        super().__init__(coordinator)
        self._level = level
        self._boost = boost
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = key
        self._attr_icon = icon

    async def async_press(self) -> None:
        """Apply the selected level and clear/set the 600-second boost timer."""
        await self.coordinator.write_level(self._level, self._boost)
