import pytest
import sr_framework.utils.helpers
from sr_framework.device.ble import BleInterface


def test_ble_gap_central_disc_0003(dut, remote):
    """Check discovery procedure response format with Raw advertising data response. """
    # GIVEN
    remote_bdaddr = remote.ble_get_local_address()
    # WHEN
    adv_data = [0x02, 0x01, 0x06, 0x05, 0x09, 0x54, 0x65, 0x73, 0x74]
    assert remote.ble_set_advertising_enable(True, adv_data)
    # THEN
    scan_raw_results = dut.ble_scan(5, BleInterface.SCAN_RESULT_FORMAT_RAW_DATA)
    assert [res for res in scan_raw_results if (res.addr == remote_bdaddr.addr) and (res.addr_type ==
            remote_bdaddr.addr_type) and sr_framework.utils.helpers.contains_sublist(res.raw_data, adv_data)]
