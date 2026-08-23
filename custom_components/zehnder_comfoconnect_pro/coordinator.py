from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .api import ComfoError


class ComfoCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, client):
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self):
        try:
            return await self.hass.async_add_executor_job(self.client.read_all)
        except ComfoError as error:
            raise UpdateFailed(str(error)) from error

    async def write_level(self, level, boost=False):
        await self.hass.async_add_executor_job(self.client.write_level, level, boost)
        await self.async_request_refresh()

    async def write_profile(self, profile):
        await self.hass.async_add_executor_job(self.client.write_profile, profile)
        await self.async_request_refresh()
