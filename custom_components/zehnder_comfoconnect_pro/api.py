"""Small synchronous Modbus client for the documented ComfoConnect PRO map."""

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import COILS, DISCRETE_INPUTS, HOLDING_REGISTERS, INPUT_REGISTERS


class ComfoError(Exception):
    """Raised when the gateway cannot complete a Modbus request."""


def signed(value):
    return value - 65536 if value >= 32768 else value


class ComfoClient:
    def __init__(self, host, port, unit_id):
        self.client = ModbusTcpClient(host, port=port, timeout=5, retries=1)
        self.unit_id = unit_id

    def close(self):
        self.client.close()

    def _request(self, operation, *, response_attribute=None):
        last_error = None
        for _attempt in range(2):
            try:
                if not self.client.connected and not self.client.connect():
                    raise ComfoError("Could not connect to Zehnder")
                response = operation()
                if response is None or response.isError():
                    raise ComfoError(str(response))
                if response_attribute and not getattr(
                    response, response_attribute, None
                ):
                    raise ComfoError(f"Zehnder returned no {response_attribute}")
                return response
            except (ComfoError, ModbusException, OSError) as error:
                last_error = error
                self.client.close()
        raise ComfoError(str(last_error) or "Zehnder request failed") from last_error

    def _read_registers(self, address, count, input_register):
        method = (
            self.client.read_input_registers
            if input_register
            else self.client.read_holding_registers
        )
        response = self._request(
            lambda: method(address=address, count=count, device_id=self.unit_id),
            response_attribute="registers",
        )
        values = [int(value) for value in response.registers[:count]]
        if len(values) != count:
            raise ComfoError(f"Zehnder returned {len(values)} of {count} registers")
        return values

    def _read(self, address, input_register):
        return self._read_registers(address, 1, input_register)[0]

    def _read_bits(self, address, count, discrete_input):
        method = (
            self.client.read_discrete_inputs
            if discrete_input
            else self.client.read_coils
        )
        response = self._request(
            lambda: method(address=address, count=count, device_id=self.unit_id),
            response_attribute="bits",
        )
        values = [bool(value) for value in response.bits[:count]]
        if len(values) != count:
            raise ComfoError(f"Zehnder returned {len(values)} of {count} bits")
        return values

    def read_all(self):
        """Read every documented register in four contiguous requests."""
        data = {}
        input_values = self._read_registers(0, 26, True)
        holding_values = self._read_registers(0, 5, False)
        discrete_values = self._read_bits(0, 4, True)
        coil_values = self._read_bits(0, 9, False)
        for key, (
            address,
            scale,
            _unit,
            _device_class,
            is_signed,
        ) in INPUT_REGISTERS.items():
            raw = input_values[address]
            data[key] = (signed(raw) if is_signed else raw) * scale
        for key, (
            address,
            scale,
            _unit,
            _device_class,
            is_signed,
        ) in HOLDING_REGISTERS.items():
            raw = holding_values[address]
            data[key] = (signed(raw) if is_signed else raw) * scale
        for key, (address, _device_class, _icon) in DISCRETE_INPUTS.items():
            data[key] = discrete_values[address]
        for key, (address, _device_class, _icon) in COILS.items():
            data[key] = coil_values[address]
        return data

    def write_level(self, level, boost=False):
        self._write(0, level)
        if boost:
            self._write(4, 600)
            self._write_coil(6, True)

    def write_profile(self, profile):
        self._write(1, profile)

    def reset_errors(self):
        self._write_coil(0, True)

    def _write(self, address, value):
        self._request(
            lambda: self.client.write_register(
                address=address, value=value, device_id=self.unit_id
            )
        )

    def _write_coil(self, address, value):
        self._request(
            lambda: self.client.write_coil(
                address=address, value=value, device_id=self.unit_id
            )
        )
