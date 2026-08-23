from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from .api import ComfoClient
from .const import CONF_UNIT_ID, PLATFORMS
from .coordinator import ComfoCoordinator


async def async_setup_entry(hass, entry: ConfigEntry):
    coordinator = ComfoCoordinator(
        hass,
        ComfoClient(
            entry.data[CONF_HOST], entry.data[CONF_PORT], entry.data[CONF_UNIT_ID]
        ),
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry):
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        entry.runtime_data.client.close()
    return unloaded
