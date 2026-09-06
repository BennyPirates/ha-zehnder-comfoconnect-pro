"""Tests for the synchronous ComfoConnect Modbus client."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


class FakeModbusException(Exception):
    """Stand-in for pymodbus.exceptions.ModbusException."""


def load_api_module():
    """Load api.py without requiring a full Home Assistant installation."""
    root = Path(__file__).parents[1]
    package_name = "custom_components.zehnder_comfoconnect_pro"

    package = types.ModuleType(package_name)
    package.__path__ = [str(root / "custom_components" / "zehnder_comfoconnect_pro")]
    sys.modules[package_name] = package

    client_module = types.ModuleType("pymodbus.client")
    client_module.ModbusTcpClient = object
    exceptions_module = types.ModuleType("pymodbus.exceptions")
    exceptions_module.ModbusException = FakeModbusException
    pymodbus_module = types.ModuleType("pymodbus")
    pymodbus_module.client = client_module
    pymodbus_module.exceptions = exceptions_module
    sys.modules["pymodbus"] = pymodbus_module
    sys.modules["pymodbus.client"] = client_module
    sys.modules["pymodbus.exceptions"] = exceptions_module

    module_name = f"{package_name}.api"
    spec = importlib.util.spec_from_file_location(
        module_name,
        root / "custom_components" / "zehnder_comfoconnect_pro" / "api.py",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


api = load_api_module()


class Response:
    def __init__(self, registers=None, error=False):
        self.registers = registers
        self._error = error

    def isError(self):
        return self._error


class FakeClient:
    def __init__(self, outcomes):
        self.connected = True
        self.outcomes = iter(outcomes)
        self.close_calls = 0
        self.connect_calls = 0
        self.read_calls = 0

    def close(self):
        self.close_calls += 1
        self.connected = False

    def connect(self):
        self.connect_calls += 1
        self.connected = True
        return True

    def read_input_registers(self, **_kwargs):
        self.read_calls += 1
        outcome = next(self.outcomes)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    read_holding_registers = read_input_registers

    def write_register(self, **_kwargs):
        outcome = next(self.outcomes)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class ComfoClientReconnectTest(unittest.TestCase):
    def test_read_reconnects_after_transport_error(self):
        fake = FakeClient(
            [FakeModbusException("connection lost"), Response(registers=[123])]
        )
        with patch.object(api, "ModbusTcpClient", return_value=fake):
            client = api.ComfoClient("gateway", 502, 1)

        self.assertEqual(client._read(6, True), 123)
        self.assertEqual(fake.read_calls, 2)
        self.assertEqual(fake.close_calls, 1)
        self.assertEqual(fake.connect_calls, 1)

    def test_read_reconnects_after_error_response(self):
        fake = FakeClient([Response(error=True), Response(registers=[42])])
        with patch.object(api, "ModbusTcpClient", return_value=fake):
            client = api.ComfoClient("gateway", 502, 1)

        self.assertEqual(client._read(6, True), 42)
        self.assertEqual(fake.close_calls, 1)
        self.assertEqual(fake.connect_calls, 1)

    def test_read_raises_comfo_error_after_retry_fails(self):
        fake = FakeClient(
            [FakeModbusException("first"), FakeModbusException("second")]
        )
        with patch.object(api, "ModbusTcpClient", return_value=fake):
            client = api.ComfoClient("gateway", 502, 1)

        with self.assertRaises(api.ComfoError):
            client._read(6, True)
        self.assertEqual(fake.read_calls, 2)
        self.assertEqual(fake.close_calls, 2)
        self.assertEqual(fake.connect_calls, 1)

    def test_write_reconnects_after_transport_error(self):
        fake = FakeClient([OSError("connection reset"), Response()])
        with patch.object(api, "ModbusTcpClient", return_value=fake):
            client = api.ComfoClient("gateway", 502, 1)

        client._write(0, 2)
        self.assertEqual(fake.close_calls, 1)
        self.assertEqual(fake.connect_calls, 1)


if __name__ == "__main__":
    unittest.main()
