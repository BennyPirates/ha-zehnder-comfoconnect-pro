import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from .api import ComfoClient, ComfoError
from .const import CONF_UNIT_ID, DEFAULT_PORT, DEFAULT_UNIT_ID, DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{user_input[CONF_UNIT_ID]}"
            )
            self._abort_if_unique_id_configured()
            client = ComfoClient(
                user_input[CONF_HOST], user_input[CONF_PORT], user_input[CONF_UNIT_ID]
            )
            try:
                await self.hass.async_add_executor_job(client.read_all)
            except ComfoError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title="Zehnder ComfoConnect Pro", data=user_input
                )
            finally:
                client.close()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Required(CONF_UNIT_ID, default=DEFAULT_UNIT_ID): vol.All(
                        int, vol.Range(min=1, max=247)
                    ),
                }
            ),
            errors=errors,
        )
