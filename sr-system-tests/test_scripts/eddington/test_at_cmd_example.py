import pytest
import re
import time
'''
@pytest.mark.parametrize("scan_type, scan_interval, scan_window, expected",
    [
        ('0',   '80',   '48',       'OK'),
        #('0',   'A',    '4',        '+CME ERROR: 916'),
        #('',    '80',   '80',       '+CME ERROR: 917'),
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


def test_abc(dut):
    dut._serial.serial_rx_clear()
    start = time.clock()
    print('{0:0.3f}'.format(start))
    dut._serial.serial_write_data('AT\r')
    regex = r"\r\n(OK)\r\n"
    resp = dut._serial.serial_search_regex(regex, 2)
    end1 = time.clock()
    count_time = end1
    print('{0:0.3f}'.format(count_time))
    dut._serial.serial_rx_clear()
    dut._serial.serial_write_data('AT\r')
    regex = r"\r\n(OK)\r\n"
    resp = dut._serial.serial_search_regex(regex, 2)
    end2 = time.clock()
    count_time = end2
    print('{0:0.3f}'.format(count_time))
    assert resp[0] == "OK"

def test_abc():
    list1 = [1, 2, 3]
    list2 = [2,3,4,5,6]
    assert len(list2) < len(list1)


@pytest.mark.parametrize("extra_characters, expected",
    [
        (['', 'a', 'A', 'AZ', '!', '@', '1', '2', '100'],         'ERROR'),
        (['1', '2'],         '+CME ERROR: 916')
    ])
def test_at_cmd_example(dut, extra_characters, expected):
    """Example script for AT command syntax test."""
    # Set BLE scan parameters
    command = '+SRBLECLOSE'

    for extra_character in extra_characters:
        dut._serial.serial_rx_clear()
        dut._serial.serial_write_data('AT{}=?{}\r'.format(command, extra_character))
        regex = r"\r\n(%s)\r\n" % re.escape(expected)
        resp = dut._serial.serial_search_regex(regex, 2)
        assert resp[0] == expected

@pytest.mark.parametrize("extra_character, expected",
    [
        ('',         'ERROR'),
        ('a',     'ERROR'),
        ('A',    'ERROR'),
        ('AZ',  'ERROR'),
        ('!',      'ERROR'),
        ('@',   'ERROR'),
        ('1',       'ERROR'),
        ('2',      'ERROR'),
        ('100',  'ERROR')
    ])
def test_at_cmd_123(dut, extra_character, expected):
    """Example script for AT command syntax test."""
    # Set BLE scan parameters
    command = '+SRBLECLOSE'
    dut._serial.serial_rx_clear()
    dut._serial.serial_write_data('AT{}{}\r'.format(command, extra_character))
    regex = r"\r\n(%s)\r\n" % re.escape(expected)
    resp = dut._serial.serial_search_regex(regex, 2)
    assert resp[0] == expected
'''

@pytest.mark.parametrize("args, expected",
    [
        (['-1,0', '-1,1'],    'ERROR'),
         # invalid duration
        #(['1'],                  [-1, 2, 'a',  'A',  '!', '@', '$'],                     'ERROR'),
         # invalid scan result format
        #([''],               ['0', '1'],               'ERROR'),
        #(['1', '2'],         [''],                     'ERROR'),
    ])
def test_at_cmd_example(dut, args, expected):
    """Example script for AT command syntax test."""
    # Set BLE scan parameters
    command = '+SRBLESCAN'

    for arg in args:
        dut._serial.serial_rx_clear()
        dut._serial.serial_write_data('AT{}={}\r'.format(command, arg))
        regex = r"\r\n(%s)\r\n" % re.escape(expected)
        resp = dut._serial.serial_search_regex(regex, 2)
        assert resp[0] == expected
