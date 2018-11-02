import pytest
import re

@pytest.mark.parametrize("scan_type, scan_interval, scan_window, expected",
    [
        ('0',   '80',   '48',       'OK'),
        ('0',   'A',    '4',        '+CME ERROR: 916'),
        ('',    '80',   '80',       '+CME ERROR: 917'),
        # insert more combinations here...
    ])
def test_at_cmd_example(dut, scan_type, scan_interval, scan_window, expected):
    """Example script for AT command syntax test."""
    # Set BLE scan parameters
    dut._serial.serial_rx_clear()
    dut._serial.serial_write_data('AT+SRBLESCANPARAMS={},{},{}\r'.format(scan_type, scan_interval, scan_window))
    regex = r"\r\n(%s)\r\n" % re.escape(expected)
    resp = dut._serial.serial_search_regex(regex, 2)
    assert resp[0] == expected
    # Get BLE scan parameters
    if expected == 'OK':
        dut._serial.serial_rx_clear()
        dut._serial.serial_write_data('AT+SRBLESCANPARAMS?\r')
        resp = dut._serial.serial_search_regex(r"\r\n\+SRBLESCANPARAMS: (\d+),(\d+),(\d+)\r\n", 2)
        assert resp[0] == scan_type
        assert resp[1] == scan_interval
        assert resp[2] == scan_window
        resp = dut._serial.serial_search_regex(r"(\r\nOK\r\n)", 2)
        assert resp