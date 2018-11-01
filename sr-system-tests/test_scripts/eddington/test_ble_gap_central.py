import pytest
#from expects import *
#from pytest_expect import expect
from sr_framework.device.ble import BleInterface
from sr_framework.device.ble import GapInterface

'''
def test_ble_gap_disc_0005(dut, remote):
    """Check discovery procedure with Passive scanning. """
    # GIVEN
    scan_type = 0
    scan_interval = 80
    scan_window = 48
    adv_data = [0x02, 0x01, 0x06, 0x05, 0x09, 0x54, 0x65, 0x73, 0x74]
    scan_resp_data = [0x05, 0x14, 0xAA, 0xBB, 0xCC, 0xDD]
    local_address = dut.ble_get_local_address()
    # WHEN
    assert dut.ble_set_scan_parameters(scan_type, scan_interval, scan_window)
    dut_scan_parameter = GapInterface.ScanParameter(scan_type, scan_interval, scan_window)
    assert dut_scan_parameter.__eq__(dut.ble_get_scan_parameters())
    assert remote.ble_set_advertising_enable(True, adv_data, scan_resp_data) is False

    # THEN
    scan_result = dut.ble_scan(10, 1)
    print(scan_result[0].addr)
    #print(len(scan_result))
    #print(scan_result)
    remote_address = remote.ble_get_local_address()
    print(remote_address.addr)
    flag_found_remote = False
    for scanned_device in scan_result:
        print(scanned_device)
        scanned_device_addr = scanned_device.addr
        if remote_address.addr == scanned_device.addr:
            flag_found_remote = True
            assert bytearray(adv_data) in scanned_device.raw_data
            assert bytearray(scan_resp_data) not in scanned_device.raw_data
    assert flag_found_remote
'''
'''
def test_melody_ble_set_advertising_enable(remote):
    adv_data = [0x02, 0x01, 0x06, 0x05, 0x09, 0x54, 0x65, 0x73, 0x74]
    #adv_data = '020106050954657374'
    scan_resp_data = [0x05, 0x14, 0xAA, 0xBB, 0xCC, 0xDD]
    command = 'ADVERTISING'
    BC127_EOL = '\r'
    args = ['{}'.format(len(adv_data))]
    remote._execute(command, args, success_string='PENDING')
    remote._send_raw_data(adv_data)
    remote._serial.serial_search_regex('(OK)', 1000)

    remote._serial.serial_write_data(BC127_EOL)
    remote._serial.serial_read_thread_start()
    #remote._serial.serial_search_regex('(ERROR)', 1000)
    command = 'SSRD'
    remote._execute(command, args, success_string='PENDING')
    remote._send_raw_data(scan_resp_data)
    remote._serial.serial_search_regex('(OK)', 1000)
    remote._serial.serial_write_data(BC127_EOL)
    remote._serial.serial_read_thread_start()
    assert remote.ble_set_advertising_enable(True, adv_data, scan_resp_data)
'''

def test_AT_SRBLESCAN_EX_0001(dut, expect):
    """Check syntax of AT+SRBLESCAN Execute command. """

    # GIVEN
    command = '+SRBLESCAN'

    # WHEN
    extra_characters = ['a', 'A', 'AZ', '!', '@', '1', '2', '100']
    RESULT_DEFAULT_ERROR = 2

    # THEN
    expect(dut._execute(command) is RESULT_DEFAULT_ERROR)
    for extra_character in extra_characters:
        command_with_extra_character = '{}{}'.format(command, extra_character)
        expect(dut._execute(command_with_extra_character) is RESULT_DEFAULT_ERROR)

def test_AT_SRBLESCAN_RD_0001(dut, expect):
    """Check syntax of AT+SRBLESCAN Read command. """

    # GIVEN
    command = '+SRBLESCAN'

    # WHEN
    extra_characters = ['a', 'A', 'AZ', '!', '@', '1', '2', '100']
    RESULT_DEFAULT_ERROR = 2
    expected = "ERROR"

    # THEN
    expect(dut._query(command) is RESULT_DEFAULT_ERROR)
    for extra_charater in extra_characters:
        dut._serial.serial_rx_clear()
        dut._serial.serial_write_data('AT{}?{}'.format(command, extra_charater) + '\r')
        regex = r"\r\n(%s)\r\n" % expected
        resp = dut._serial.serial_search_regex(regex, 2)
        expect(resp[0] == expected)

def test_AT_SRBLESCAN_TS_0001(dut, expect):
    """Check syntax of AT+SRBLESCAN Test command. """

    # GIVEN
    command = '+SRBLESCAN'

    # WHEN
    extra_characters = ['a', 'A', 'AZ', '!', '@', '1', '2', '100']
    RESULT_DEFAULT_ERROR = 2

    # THEN
    expect(dut._test(command) is RESULT_DEFAULT_ERROR)
    for extra_charater in extra_characters:
        dut._serial.serial_rx_clear()
        dut._serial.serial_write_data('AT{}=?{}'.format(command, extra_charater) + '\r')
        regex = r"\r\n(.*)\r\n"
        resp = dut._serial.serial_search_regex(regex, 2)
        expect(resp[0] is RESULT_DEFAULT_ERROR)
'''
def test_AT_SRBLESCAN_WR_0001(dut):
    """Check syntax of AT+SRBLESCAN Write command. """

    # GIVEN
    dut._enable_bluetooth()
    command = '+SRBLESCAN'

    # WHEN
    durations = ['a',  'A',  '!', '@', '$', '-1', '0', '65536']
    result_formats = [0, 1]

    # THEN
    for duration in durations:
        for result_format in result_formats:
            args = [duration, result_format]
            expect(dut._write_invalid_command(command, args) == '916')

    # WHEN
    durations = [1]
    result_formats = ['-1', '2', 'a',  'A',  '!', '@', '$']

    # THEN
    for duration in durations:
        for result_format in result_formats:
            args = [duration, result_format]
            expect(dut._write_invalid_command(command, args) == '916')

    # WHEN
    duration = ''
    result_formats = ['0', '1']

    # THEN
    for result_format in result_formats:
        args = [duration, result_format]
        error_message = dut._write_invalid_command(command, args)
        expect(error_message == '917')
    
    # WHEN
    durations = ['1', '2', '65535']
    result_format = ''

    # THEN
    for duration in durations:
         args = [duration, result_format]
         expect(dut._write_invalid_command(command, args) == '917')
    args = [duration]
    expect(dut._write_invalid_command(command, args) == '917')

    # WHEN
    duration = '1'
    result_format = '0'
    extra_parameter = ['1', 'a', '!']

    expect('915' == '915')
    expect('916' == '915')
    expect('917' == '915')
    # THEN
    args = [duration, result_format, '1']
    expect(dut._write_invalid_command(command, args) == '915')
    expect(dut._write_invalid_command(command, args) == '915')
    expect(dut._write_invalid_command(command, args) == '915')
    


def test_justTest(dut):
    response = dut.common_reset()
    print(type(response))
'''