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
    def __init__(self, registers=None, bits=None, error=False):
        self.registers = registers
        self.bits = bits
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
        self.write_calls = []

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

    read_discrete_inputs = read_input_registers
    read_coils = read_input_registers

    def write_register(self, **kwargs):
        self.write_calls.append(("register", kwargs))
        outcome = next(self.outcomes)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    def write_coil(self, **kwargs):
        self.write_calls.append(("coil", kwargs))
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
        fake = FakeClient([FakeModbusException("first"), FakeModbusException("second")])
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

    def test_read_all_reads_complete_map_in_four_requests(self):
        input_registers = [0, 77, 0, 0, 0, 0, 180, 215, 210, 50, 65526]
        input_registers.extend([220, 40, 50, 60, 70, 80])
        input_registers.extend([400, 500, 600, 700, 800, 900, 1000, 1100, 123])
        fake = FakeClient(
            [
                Response(registers=input_registers),
                Response(registers=[2, 1, 0, 215, 600]),
                Response(bits=[False, False, False, True]),
                Response(
                    bits=[False, False, False, True, False, True, False, False, True]
                ),
            ]
        )
        with patch.object(api, "ModbusTcpClient", return_value=fake):
            client = api.ComfoClient("gateway", 502, 1)

        data = client.read_all()

        self.assertEqual(fake.read_calls, 4)
        self.assertEqual(data["active_error_1"], 77)
        self.assertEqual(data["outdoor_air_temperature"], -1.0)
        self.assertEqual(data["filter_days_remaining"], 123)
        self.assertTrue(data["filter_replacement_required"])
        self.assertTrue(data["auto_mode_active"])
        self.assertTrue(data["comfocool_active"])

    def test_boost_uses_documented_duration_register_and_activation_coil(self):
        fake = FakeClient([Response(), Response(), Response()])
        with patch.object(api, "ModbusTcpClient", return_value=fake):
            client = api.ComfoClient("gateway", 502, 1)

        client.write_level(3, boost=True)

        self.assertEqual(
            fake.write_calls,
            [
                ("register", {"address": 0, "value": 3, "device_id": 1}),
                ("register", {"address": 4, "value": 600, "device_id": 1}),
                ("coil", {"address": 6, "value": True, "device_id": 1}),
            ],
        )

    def test_reset_errors_writes_self_resetting_coil(self):
        fake = FakeClient([Response()])
        with patch.object(api, "ModbusTcpClient", return_value=fake):
            client = api.ComfoClient("gateway", 502, 1)

        client.reset_errors()

        self.assertEqual(
            fake.write_calls,
            [("coil", {"address": 0, "value": True, "device_id": 1})],
        )


if __name__ == "__main__":
    unittest.main()
