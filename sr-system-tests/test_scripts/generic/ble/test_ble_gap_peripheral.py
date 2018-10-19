import pytest
import sr_framework.utils.helpers
from sr_framework.device.ble import BleInterface
import time
import warnings


def test_ble_gap_peripheral_disc_02_1(dut, remote):
    """Verify DUT can start advertising. """
    # GIVEN
    dut_bdaddr = dut.ble_get_local_address()
    # WHEN
    assert dut.ble_set_advertising_enable(True)
    # THEN
    scan_results = remote.ble_scan(10)
    assert [res for res in scan_results if (
        res.addr == dut_bdaddr.addr) and (res.addr_type == dut_bdaddr.addr_type)]


def test_ble_gap_peripheral_disc_02_2(dut, remote):
    """Verify DUT advertising can stop advertising. """
    # GIVEN
    dut_bdaddr = dut.ble_get_local_address()
    assert dut.ble_set_advertising_enable(True)
    # WHEN
    assert dut.ble_set_advertising_enable(False)
    # THEN
    scan_results = remote.ble_scan(10)
    assert not [res for res in scan_results if (
        res.addr == dut_bdaddr.addr) and (res.addr_type == dut_bdaddr.addr_type)]


def test_ble_gap_peripheral_disc_03_3(dut, remote):
    """Verify DUT can set the advertising data. """
    # GIVEN
    dut_bdaddr = dut.ble_get_local_address()
    # WHEN
    adv_data = [0x02, 0x01, 0x06, 0x05, 0x09, 0x54, 0x65, 0x73, 0x74]
    assert dut.ble_set_advertising_enable(True, adv_data)
    # THEN
    scan_raw_results = remote.ble_scan(10, BleInterface.SCAN_RESULT_FORMAT_RAW_DATA)
    assert [res for res in scan_raw_results if(res.addr == dut_bdaddr.addr) and (
        res.addr_type == dut_bdaddr.addr_type) and sr_framework.utils.helpers.contains_sublist(res.raw_data, adv_data)]


def test_ble_gap_peripheral_disc_04(dut, remote):
    """Verify DUT can set the scan response data. """
    # GIVEN
    dut_bdaddr = dut.ble_get_local_address()
    # WHEN
    adv_data = [0x02, 0x01, 0x06, 0x05, 0x09, 0x54, 0x65, 0x73, 0x74]
    scan_resp_data = [0x05, 0x14, 0xAA, 0xBB, 0xCC, 0xDD]
    assert dut.ble_set_advertising_enable(True, adv_data, scan_resp_data)
    # THEN
    scan_raw_results = remote.ble_scan(10, True)
    assert [res for res in scan_raw_results if (res.addr == dut_bdaddr.addr) and (
        res.addr_type == dut_bdaddr.addr_type) and sr_framework.utils.helpers.contains_sublist(res.raw_data, adv_data)]
    assert [res for res in scan_raw_results if (res.addr == dut_bdaddr.addr) and (
        res.addr_type == dut_bdaddr.addr_type) and sr_framework.utils.helpers.contains_sublist(res.raw_data, scan_resp_data)]


def test_ble_gap_peripheral_disc_05_2(dut):
    """Verify DUT can set the advertising parameters. """
    # GIVEN
    'N/A'
    # WHEN
    assert dut.ble_set_advertising_parameters(
        BleInterface.ADV_TYPE_DIRECT_IND_HIGH, 0x20, 0x40, 18000, BleInterface.ADV_FP_ANY)
    # THEN
    warnings.warn('TODO: Add LeGetAdvertisingParameters method.')


def test_ble_gap_peripheral_conn_02(dut, remote):
    """Verify DUT advertising can accept connection from BLE Central device. """
    # GIVEN
    dut_bdaddr = dut.ble_get_local_address()
    remote_bdaddr = remote.ble_get_local_address()
    assert dut.ble_set_advertising_enable(True)
    # WHEN
    remote_session = remote.ble_create_session(dut_bdaddr)
    assert remote.ble_connect(remote_session.session_id)
    assert dut.ble_wait_for_connection()
    # THEN
    dut_session_id = dut.ble_get_session_id_from_bdaddr(remote_bdaddr)
    assert dut_session_id is not None
    assert dut.ble_is_connected(dut_session_id)
    assert remote.ble_is_connected(remote_session.session_id)


def test_ble_gap_peripheral_conn_03(dut, remote):
    """Verify DUT connected to a BLE Central device can disconnect. """
    # GIVEN
    dut_bdaddr = dut.ble_get_local_address()
    remote_bdaddr = remote.ble_get_local_address()
    assert dut.ble_set_advertising_enable(True)
    remote_session = remote.ble_create_session(dut_bdaddr)
    assert remote.ble_connect(remote_session.session_id)
    assert dut.ble_wait_for_connection()
    dut_session_id = dut.ble_get_session_id_from_bdaddr(remote_bdaddr)
    assert dut_session_id is not None 
    assert dut.ble_is_connected(dut_session_id)
    assert remote.ble_is_connected(remote_session.session_id)
    # WHEN
    assert dut.ble_disconnect(dut_session_id)
    assert remote.ble_wait_for_disconnection(remote_session.session_id)
    # THEN
    assert not dut.ble_is_connected(dut_session_id)
    assert not remote.ble_is_connected(remote_session.session_id)


def test_ble_gap_peripheral_conn_04_2(dut):
    """Verify DUT can set the GAP peripheral preferred connection parameters. """
    # GIVEN
    'N/A'
    # WHEN
    assert dut.ble_set_peripheral_preferred_connection_parameters(40, 400, 0, 500)
    # THEN
    warnings.warn(
        'TODO: Add LeGetPeripheralPreferredConnectionParameters method.')
