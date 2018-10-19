import pytest
from sr_framework.device.ble import BleInterface


def test_ble_bdaddr(dut):
    """Verify DUT can returns its Bluetooth address. """
    # GIVEN
    'N/A'
    # WHEN
    typed_bdaddr = dut.ble_get_local_address()
    # THEN
    assert typed_bdaddr is not None


def test_ble_session_01(dut):
    """Verify DUT can create up to 16 BLE sessions. """
    # GIVEN
    'N/A'
    # WHEN
    for i in range(0, 15):
        addr = '20:FA:BB:00:00:{:02X}'.format(i)
        session = dut.ble_create_session(
            BleInterface.Bdaddr(addr, BleInterface.LE_BDADDR_TYPE_PUBLIC))
        assert session.session_id == (i + 1)
        assert session.bdaddr.addr == addr
    # THEN
    'N/A'


def test_ble_session_02(dut):
    """Verify DUT can list all the BLE sessions. """
    # GIVEN
    a = dut.ble_create_session(BleInterface.Bdaddr(
        '20:FA:BB:00:00:AA', BleInterface.LE_BDADDR_TYPE_PUBLIC))
    assert a is not None
    b = dut.ble_create_session(BleInterface.Bdaddr(
        '11:22:33:44:55:66', BleInterface.LE_BDADDR_TYPE_PRIVATE))
    assert b is not None
    c = dut.ble_create_session(BleInterface.Bdaddr(
        '77:88:99:AA:BB:CC', BleInterface.LE_BDADDR_TYPE_PRIVATE))
    assert c is not None
    # WHEN
    list = dut.ble_get_all_sessions()
    # THEN
    assert a in list
    assert b in list
    assert c in list


def test_ble_session_03(dut):
    """Verify DUT can delete an existing BLE session. """
    # GIVEN
    a = dut.ble_create_session(BleInterface.Bdaddr(
        '20:FA:BB:00:00:AA', BleInterface.LE_BDADDR_TYPE_PUBLIC))
    assert a is not None
    b = dut.ble_create_session(BleInterface.Bdaddr(
        '11:22:33:44:55:66', BleInterface.LE_BDADDR_TYPE_PRIVATE))
    assert b is not None
    c = dut.ble_create_session(BleInterface.Bdaddr(
        '77:88:99:AA:BB:CC', BleInterface.LE_BDADDR_TYPE_PRIVATE))
    assert c is not None
    # WHEN
    assert dut.ble_delete_session(b.session_id)
    # THEN
    list = dut.ble_get_all_sessions()
    assert a in list
    assert b not in list
    assert c in list
