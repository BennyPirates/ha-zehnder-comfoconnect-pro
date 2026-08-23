"""Small synchronous Modbus client; writes are strictly limited to documented controls."""

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from .const import HOLDING_REGISTERS, INPUT_REGISTERS


class ComfoError(Exception):
    pass


def signed(value):
    return value - 65536 if value >= 32768 else value


class ComfoClient:
    def __init__(self, host, port, unit_id):
        self.client = ModbusTcpClient(host, port=port, timeout=5, retries=1)
        self.unit_id = unit_id

    def close(self):
        self.client.close()

    def _read(self, address, input_register):
        if not self.client.connected and not self.client.connect():
            raise ComfoError("Could not connect to Zehnder")
        response = (
            self.client.read_input_registers
            if input_register
            else self.client.read_holding_registers
        )(address=address, count=1, device_id=self.unit_id)
        if response.isError() or not response.registers:
            raise ComfoError(str(response))
        return int(response.registers[0])

    def read_all(self):
        data = {}
        for key, (address, scale, *_) in INPUT_REGISTERS.items():
            data[key] = signed(self._read(address, True)) * scale
        for key, (address, scale, *_) in HOLDING_REGISTERS.items():
            data[key] = self._read(address, False) * scale
        return data

    def write_level(self, level, boost=False):
        self._write(0, level)
        self._write(4, 600 if boost else 0)

    def write_profile(self, profile):
        self._write(1, profile)

    def _write(self, address, value):
        try:
            response = self.client.write_register(
                address=address, value=value, device_id=self.unit_id
            )
        except (ModbusException, OSError) as error:
            raise ComfoError(str(error)) from error
        if response.isError():
            raise ComfoError(str(response))
