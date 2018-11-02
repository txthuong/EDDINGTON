import pytest
import re
import time
'''
@pytest.mark.parametrize("extra_characters, expected",
    [
        (['', 'a', 'A', 'AZ', '!', '@', '1', '2', '100'],       'ERROR')
    ])
def test_at_srblescanparams_ex_0001(dut, extra_characters,  expected):
    """Check syntax of AT+SRBLESCANPARAMS Execute command."""
    # GIVEN
    command = '+SRBLESCANPARAMS'
    time.sleep(1)
    # WHEN
    for extra_character in extra_characters:
        dut._serial.serial_rx_clear()
        dut._serial.serial_write_data('AT{}{}\r'.format(command, extra_character))
        regex = r"\r\n(%s)\r\n" % re.escape(expected)
        resp = dut._serial.serial_search_regex(regex, 2)
        assert resp[0] == expected
    # THEN
    'N/A'


@pytest.mark.parametrize("extra_characters, expected",
    [
        ([''],                                                        'ERROR'),
        (['a', 'A', 'AZ', '!', '@', '1', '2', '100'],       '+CME ERROR: 916')
    ])
def test_at_srblescanparams_ts_0001(dut, extra_characters,  expected):
    """Check syntax of AT+SRBLESCANPARAMS Execute command."""
    # GIVEN
    command = '+SRBLESCANPARAMS'
    dut._serial.serial_rx_clear()
    time.sleep(1)
    # WHEN
    for extra_character in extra_characters:
        dut._serial.serial_rx_clear()
        dut._serial.serial_write_data('AT{}=?{}\r'.format(command, extra_character))
        regex = r"\r\n(%s)\r\n" % re.escape(expected)
        resp = dut._serial.serial_search_regex(regex, 2)
        assert resp[0] == expected
    # THEN
    'N/A'


@pytest.mark.parametrize("extra_characters, expected",
    [
        ([''],                                                 'OK'),
        (['a', 'A', 'AZ', '!', '@', '1', '2', '100'],       'ERROR')
    ])
def test_at_srblescanparams_rd_0001(dut, extra_characters,  expected):
    """Check syntax of AT+SRBLESCANPARAMS Execute command."""
    # GIVEN
    command = '+SRBLESCANPARAMS'
    time.sleep(1)
    # WHEN
    for extra_character in extra_characters:
        dut._serial.serial_rx_clear()
        dut._serial.serial_write_data('AT{}?{}'.format(command, extra_character) + '\r')
        if expected == 'OK':
            resp = dut._serial.serial_search_regex(r"\r\n\+SRBLESCANPARAMS: (\d+),(\d+),(\d+)\r\n", 2)
            assert resp
            resp = dut._serial.serial_search_regex(r"(\r\nOK\r\n)", 2)
            assert resp
        else:
            regex = r"\r\n(%s)\r\n" % re.escape(expected)
            resp = dut._serial.serial_search_regex(regex, 2)
            assert resp[0] == expected
    # THEN
    'N/A'


@pytest.mark.parametrize("args, expected",
    [
        (['-1,80,48', '2,80,48', 'a,80,48',  'A,80,48',  '!,80,48', '@,80,48', '$,80,48'],      '+CME ERROR: 916'),
        # <scanning type> invalid; <scan interval>=[80]; <scan window> = [48]
        (['0,-3,4', '0,3,4', '0,16385,4', '0,a,4',  '0,A,4',  '0,!,4', '0,@,4', '0,$,4'],       '+CME ERROR: 916'),
        # <scanning type>= [0]; <scan interval> invalid; <scan window> = [4]
        (['1,-3,4', '1,3,4', '1,16385,4', '1,a,4',  '1,A,4',  '1,!,4', '1,@,4', '1,$,4'],       '+CME ERROR: 916'),
        # <scanning type>= [1]; <scan interval> invalid; <scan window> = [4]
        (['1,16384,-3', '1,16384,3', '1,16384,16385', '1,16384,a', '1,16384,A', '1,16384,!'],   '+CME ERROR: 916'),
        # <scanning type>= [1]; <scan interval>=[16384]; <scan window> invalid
        (['0,16384,-3', '0,16384,3', '0,16384,16385', '0,16384,a', '0,16384,A', '0,16384,!'],   '+CME ERROR: 916'),
        # <scanning type>= [0]; <scan interval>=[16384]; <scan window> invalid
        (['0,80,81', '0,80,82', '0,80,16384'],                                                  '+CME ERROR: 916'),
        # <scanning type>= [0]; <scan interval>=[80]; <scan window> is greater than <scan interval>
        (['1,80,81', '1,80,82', '1,80,16384'],                                                  '+CME ERROR: 916'),
        # <scanning type>= [1]; <scan interval>=[80]; <scan window> is greater than <scan interval>
        ([',80,48'],                                                                            '+CME ERROR: 917'),
        # Missing <scanning type> parameter
        (['0,80', '1,80', '0,80,', '1,80,'],                                                    '+CME ERROR: 917'),
        # Missing <scan interval> parameter
        (['0,,48', '1,,48'],                                                                    '+CME ERROR: 917'),
        # Missing <scan window> parameter
        (['0,80,48,1', '0,80,48,a', '0,80,48,!', '1,80,48,1', '1,80,48,a', '1,80,48,!'],        '+CME ERROR: 915'),
        # Extra parameter
        (['0,80,48'],                                                                                        'OK')
        # Valid parameter
    ])
def test_at_srblescanparams_wr_0001(dut, args, expected):
    """Check syntax of AT+SRBLESCANPARAMS Execute command."""
    # GIVEN
    command = '+SRBLESCANPARAMS'
    dut._serial.serial_rx_clear()
    time.sleep(1)
    # WHEN
    for arg in args:
        dut._serial.serial_rx_clear()
        dut._serial.serial_write_data('AT{}={}\r'.format(command, arg))
        regex = r"\r\n(%s)\r\n" % re.escape(expected)
        resp = dut._serial.serial_search_regex(regex, 2)
        assert resp[0] == expected
    # THEN
    'N/A'
'''

@pytest.mark.parametrize("args, expected",
    [
        (['-1,80,48', '2,80,48', 'a,80,48',  'A,80,48',  '!,80,48', '@,80,48', '$,80,48'],      '+CME ERROR: 916'),
        # <scanning type> invalid; <scan interval>=[80]; <scan window> = [48]
        (['0,-3,4', '0,3,4', '0,16385,4', '0,a,4',  '0,A,4',  '0,!,4', '0,@,4', '0,$,4'],       '+CME ERROR: 916'),
        # <scanning type>= [0]; <scan interval> invalid; <scan window> = [4]
        (['1,-3,4', '1,3,4', '1,16385,4', '1,a,4',  '1,A,4',  '1,!,4', '1,@,4', '1,$,4'],       '+CME ERROR: 916'),
        # <scanning type>= [1]; <scan interval> invalid; <scan window> = [4]
        (['1,16384,-3', '1,16384,3', '1,16384,16385', '1,16384,a', '1,16384,A', '1,16384,!'],   '+CME ERROR: 916'),
        # <scanning type>= [1]; <scan interval>=[16384]; <scan window> invalid
        (['0,16384,-3', '0,16384,3', '0,16384,16385', '0,16384,a', '0,16384,A', '0,16384,!'],   '+CME ERROR: 916'),
        # <scanning type>= [0]; <scan interval>=[16384]; <scan window> invalid
        (['0,80,81', '0,80,82', '0,80,16384'],                                                  '+CME ERROR: 916'),
        # <scanning type>= [0]; <scan interval>=[80]; <scan window> is greater than <scan interval>
        (['1,80,81', '1,80,82', '1,80,16384'],                                                  '+CME ERROR: 916'),
        # <scanning type>= [1]; <scan interval>=[80]; <scan window> is greater than <scan interval>
        ([',80,48'],                                                                            '+CME ERROR: 917'),
        # Missing <scanning type> parameter
        (['0,80', '1,80', '0,80,', '1,80,'],                                                    '+CME ERROR: 917'),
        # Missing <scan interval> parameter
        (['0,,48', '1,,48'],                                                                    '+CME ERROR: 917'),
        # Missing <scan window> parameter
        (['0,80,48,1', '0,80,48,a', '0,80,48,!', '1,80,48,1', '1,80,48,a', '1,80,48,!'],        '+CME ERROR: 915'),
        # Extra parameter
        (['0,80,48'],                                                                                        'OK')
        # Valid parameter
    ])
def test_at_srblescanparams_ex_0001(dut, args,  expected):
    """Check syntax of AT+SRBLESCANPARAMS Execute command."""
    # GIVEN
    command = '+SRBLESCANPARAMS'
    time.sleep(1)
    # WHEN
    for arg in args:
        resp = dut._write_error(command, arg)
        assert resp == expected  # abc
    # THEN
    'N/A'