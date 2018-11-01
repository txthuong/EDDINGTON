#!/usr/bin/python

""" melody module.
It contains the Melody class, which inherits from the Board class
and implements the common, ble and hw interfaces. """

import time
import warnings
from sr_framework.device.board import Board
from sr_framework.device.common import CommonInterface
from sr_framework.device.ble import BleInterface
from sr_framework.device.hw import HWInterface

# Melody end of line character
BC127_EOL = '\r'

# Melody default command timeout (in seconds)
DEFAULT_COMMAND_TIMEOUT = 2

# Melody result codes
BC127_RESULT_SUCCESS = 0
BC127_RESULT_ERROR = 1
BC127_RESULT_TIMEOUT = 2

# Melody configuration regex
CONFIG_DICT = {
    'BLE_CONFIG':   r"BLE_CONFIG=(\d) (ON|OFF) (\d+) (ON|OFF)" + BC127_EOL,
    'LOCAL_ADDR':   r"LOCAL_ADDR=(\w{12}) (\w{12})" + BC127_EOL,
    'UART_CONFIG':  r"UART_CONFIG=(\d{4,6}) (ON|OFF) ([0-2])" + BC127_EOL,
}

class Melody(Board, CommonInterface, BleInterface, HWInterface):
    """Melody board. Used to control BC127 over serial interface (UART)."""

    class BleSessionWrapper(BleInterface.BleSession):
        """Melody virtual BLE session."""

        def __init__(self, session_id, bdaddr):
            super().__init__(session_id, bdaddr)
            self.link_id = 0  # Melody link identifier (int)

        def __eq__(self, other):
            return (self.session_id == other.session_id) and (self.bdaddr == other.bdaddr) and \
                (self.link_id == other.link_id)

        def __ne__(self, other):
            return not self == other

        def __str__(self):
            return ('BleSessionWrapper: session_id=%d, addr="%s", type=%d, link_id=%d' %
                    (self.session_id, self.bdaddr.addr, self.bdaddr.addr_type, self.link_id))

    def __init__(self, device):
        super().__init__(device)
        self._ble_sessions = []  # virtual BLE sessions (BleSessionWrapper).

    @staticmethod
    def _convert_melody_address_to_standard(addr):
        if ':' not in addr:
            # convert "001122AABBCC" to "00:11:22:AA:BB:CC"
            addr_iter = iter(addr)
            addr = ':'.join(a + b for a, b in zip(addr_iter, addr_iter))
        return addr

    @staticmethod
    def _convert_standard_address_to_melody(addr):
        return addr.replace(':', '')

    # BLE sessions helpers
    def _ble_sessions_get_unused_session_id(self):
        for i in range(1, 16):
            already_used = False
            for session in self._ble_sessions:
                if session.session_id == i:
                    already_used = True
                    break
            if not already_used:
                return i
        return None

    def _ble_sessions_delete_all_sessions(self):
        self._ble_sessions = []

    def _ble_sessions_get_session_from_bdaddr(self, bdaddr):
        for session in self._ble_sessions:
            if session.bdaddr == bdaddr:
                return session.session_id
        return None

    def _ble_sessions_get_bdaddr_from_session_id(self, session_id):
        for session in self._ble_sessions:
            if session.session_id == session_id:
                return session.bdaddr
        return None

    def _ble_sessions_get_link_id_from_session_id(self, session_id):
        for session in self._ble_sessions:
            if session.session_id == session_id:
                return session.link_id
        return None

    def _ble_sessions_set_session_link_id(self, session_id, link_id):
        for session in self._ble_sessions:
            if session.session_id == session_id:
                session.link_id = link_id
                return True
        return False

    # Command helpers
    def _get_result_from_response(self, success_string, error_string, timeout):
        while timeout >= 0:
            if self._serial.serial_search_line_startswith(success_string):
                return BC127_RESULT_SUCCESS
            if self._serial.serial_search_line_startswith(error_string) or \
                self._serial.serial_search_line_startswith('ERROR'):
                return BC127_RESULT_ERROR
            time.sleep(min(0.1, timeout))
            timeout -= 0.1
        return BC127_RESULT_TIMEOUT

    def _execute(self,
                 command,
                 args=None,
                 success_string='OK',
                 error_string='ERROR',
                 timeout=DEFAULT_COMMAND_TIMEOUT):
        self._serial.serial_rx_clear()
        self._serial.serial_write_data(command
                                       + (' ' if (command[-1] != '=') and args else '')
                                       + (' '.join(str(x)
                                                   for x in args) if args else '')
                                       + BC127_EOL)
        return self._get_result_from_response(success_string, error_string, timeout)

    def _send_raw_data(self, data):
        #self._serial.serial_write_data(bytearray(data))
        # txthuong
        data = ''.join('{:02x}'.format(x) for x in data)
        self._serial.serial_write_data(data)

    def _set_config(self, config, args):
        command = 'SET' + ' ' + config + '='
        return self._execute(command, args) == BC127_RESULT_SUCCESS

    def _get_config(self, config):
        command = 'GET' + ' ' + config
        if self._execute(command) is BC127_RESULT_SUCCESS:
            return list(self._serial.serial_search_regex(CONFIG_DICT[config]))
        return None

    def _clear_command_buffer(self):
        return self._execute('<clear>', error_string='ERROR 0x0012') == BC127_RESULT_ERROR


    # COMMON INTERFACE.

    def common_send_custom_command(self, command):
        """Function defined in CommonInterface."""
        return self._execute(command, timeout=5) is BC127_RESULT_SUCCESS

    def common_reset(self):
        """Function defined in CommonInterface."""
        command = 'RESET'
        if self._execute(command, success_string='Ready') is BC127_RESULT_SUCCESS:
            self._ble_sessions_delete_all_sessions()
            return True
        return False

    def common_get_supported_command_list(self):
        """Function defined in CommonInterface."""
        command = 'HELP'
        if self._execute(command) is BC127_RESULT_SUCCESS:
            responses = self._serial.serial_search_regex_all(r"(\w+)" + BC127_EOL)
            return list(responses[:-1])  # remove last element 'OK'
        return None

    def common_restore_to_defaults(self):
        """Function defined in CommonInterface."""
        # Restore default config
        if self._execute('RESTORE', success_string='Ready') != BC127_RESULT_SUCCESS:
            return False
        # Clear all virtual sessions
        self._ble_sessions_delete_all_sessions()
        # Unpair all devices
        if self._execute('UNPAIR') != BC127_RESULT_SUCCESS:
            return False
        if self.common_reset() is False:
            return False
        return True

    def common_read_manufacturer_id(self):
        """Function defined in CommonInterface."""
        command = 'VERSION'
        if self._execute(command) is BC127_RESULT_SUCCESS:
            regex = r"([\w| ]+) Copyright 2018\r([\w| |\.]+)\rBuild: (\d+)"
            response = self._serial.serial_search_regex(regex)
            return response[0]
        return None

    def common_read_model_id(self):
        """Function defined in CommonInterface."""
        # There is no existing command to get the model identification.
        return 'BC127'

    def common_read_revision_id(self):
        """Function defined in CommonInterface."""
        command = 'VERSION'
        if self._execute(command) is BC127_RESULT_SUCCESS:
            regex = r"([\w| ]+) Copyright 2018\r([\w| |\.]+)\rBuild: (\d+)"
            response = self._serial.serial_search_regex(regex)
            return response[1]
        return None

    def common_get_remote_controller(self):
        """Function defined in CommonInterface."""
        warnings.warn('Not supported.')
        return 0

    def common_set_remote_controller(self, session_id):
        """Function defined in CommonInterface."""
        warnings.warn('Not supported.')
        return False


    # HARDWARE INTERFACE.

    def hw_set_uart_baudrate(self, new_baudrate):
        """Function defined in HWInterface."""
        uart_config = self._get_config('UART_CONFIG')
        args = ['{} {} {}'.format(new_baudrate, uart_config[1], uart_config[2])]
        self._set_config('UART_CONFIG', args)
        # OK is printed in the new baudrate, can't check for it.
        self.set_serial_baudrate(new_baudrate)
        return self._clear_command_buffer()

    def hw_set_uart_flow_control(self, enable):
        """Function defined in HWInterface."""
        uart_config = self._get_config('UART_CONFIG')
        if (enable and uart_config[1] == 'OFF') or (not enable and uart_config[1] == 'ON'):
            # Enable/disable Flow control (reboot required)
            args = ['{} {} {}'.format(uart_config[0], 'ON' if enable else 'OFF', uart_config[2])]
            if self._set_config('UART_CONFIG', args) is False:
                return False
            if self.hw_save_settings() is False:
                return False
            if self.common_reset() is False:
                return False
            return self.serial_flow_control(enable)
        # Nothing to do
        return True

    def hw_get_uart_baudrate(self):
        """Function defined in HWInterface."""
        uart_config = self._get_config('UART_CONFIG')
        return int(uart_config[0])

    def hw_save_settings(self):
        """Function defined in HWInterface."""
        return self._execute('WRITE') == BC127_RESULT_SUCCESS


    # BLE INTERFACE.

    def ble_get_local_address(self):
        """Function defined in BleInterface."""
        addr = Melody._convert_melody_address_to_standard(
            self._get_config('LOCAL_ADDR')[1])
        addr_type = True if self._get_config('BLE_CONFIG')[3] == 'ON' else False
        return BleInterface.Bdaddr(addr, addr_type)

    def ble_create_session(self, bdaddr):
        """Function defined in BleInterface."""
        # use virtual sessions since Melody does not have sessions.
        if self._ble_sessions_get_session_from_bdaddr(bdaddr) is None:
            ble_session = Melody.BleSessionWrapper(
                self._ble_sessions_get_unused_session_id(), bdaddr)
            self._ble_sessions.append(ble_session)
            return ble_session
        return None

    def ble_delete_session(self, session_id):
        """Function defined in BleInterface."""
        # use virtual sessions since Melody does not have sessions.
        for session in self._ble_sessions[:]:
            if session.session_id == session_id:
                self._ble_sessions.remove(session)
                return True
        return False

    def ble_get_session_id_from_bdaddr(self, bdaddr):
        """Function defined in BleInterface."""
        return self._ble_sessions_get_session_from_bdaddr(bdaddr)

    def ble_get_all_sessions(self):
        """Function defined in BleInterface."""
        # use virtual sessions since Melody does not have sessions.
        return [BleInterface.BleSession(s.session_id, s.bdaddr) for s in self._ble_sessions]


    # BLE GAP interface.

    def ble_set_advertising_enable(self, enable, adv_data=None, scan_resp_data=None):
        """Function defined in GapInterface."""
        if adv_data:
            # Set advertising data
            command = 'ADVERTISING'
            args = ['{}'.format(len(adv_data))]
            if self._execute(command, args, success_string='PENDING') is BC127_RESULT_SUCCESS:
                self._send_raw_data(adv_data)
                # txthuong
                #if not self._serial.serial_search_regex('(OK)'):
                if not self._serial.serial_search_regex('(OK)', 1000):
                    return False
            else:
                return False

        if scan_resp_data:
            # Set scan response data
            command = 'SSRD'
            args = ['{}'.format(len(scan_resp_data))]
            if self._execute(command, args, success_string='PENDING') is BC127_RESULT_SUCCESS:
                self._send_raw_data(scan_resp_data)
                # txthuong
                #if not self._serial.serial_search_regex('(OK)'):
                if not self._serial.serial_search_regex('(OK)', 1000):
                    return False
            else:
                return False
        # Start/stop advertising
        command = 'ADVERTISING'
        args = ['ON' if enable else 'OFF']
        return self._execute(command, args) is BC127_RESULT_SUCCESS

    def ble_set_advertising_parameters(self,
                                       adv_type,
                                       adv_int_min,
                                       adv_int_max,
                                       adv_timeout,
                                       adv_fp=0):
        """Function defined in GapInterface."""
        warnings.warn('TODO')
        return False

    def ble_set_peripheral_preferred_connection_parameters(self,
                                                           min_conn_interval,
                                                           max_conn_interval,
                                                           conn_latency,
                                                           supervision_timeout):
        """Function defined in GapInterface."""
        warnings.warn('Not supported.')
        return False

    def ble_scan(self, duration, result_format=BleInterface.SCAN_RESULT_FORMAT_DEFAULT):
        """Function defined in GapInterface."""
        command = 'SCAN'
        args = [duration]
        if result_format == BleInterface.SCAN_RESULT_FORMAT_DEFAULT:
            if self._execute(command,
                             args,
                             success_string='SCAN_OK',
                             timeout=duration+1) is BC127_RESULT_SUCCESS:
                regex = r"SCAN (\w{12}) (0|1) <(.+)> ([0-9A-F]{2}) -(\d+)dBm" + BC127_EOL
                responses = self._serial.serial_search_regex_all(regex)
                return [BleInterface.ScanResult( \
                                Melody._convert_melody_address_to_standard(resp[0]),
                                int(resp[1]),
                                int(resp[4]),
                                int(resp[3], 16),
                                resp[2])
                        for resp in responses]
        elif result_format == BleInterface.SCAN_RESULT_FORMAT_RAW_DATA:
            args.append('ON')
            if self._execute(command,
                             args,
                             success_string='SCAN_OK',
                             timeout=duration+1) is BC127_RESULT_SUCCESS:
                scan_raw_regex = r"SCAN_RAW (\w{12}) (\d) -(\d+)dBm (\d+) ([0-9A-F| ]+)" + BC127_EOL
                responses = self._serial.serial_search_regex_all(
                    scan_raw_regex)
                return [BleInterface.ScanRawResult( \
                               Melody._convert_melody_address_to_standard(resp[0]),
                               int(resp[1]),
                               int(resp[2]),
                               [int(x, 16) for x in resp[4].split()])
                        for resp in responses]
        else:
            raise ValueError('invalid result_format')
        return None

    def ble_set_scan_parameters(self, scan_type, scan_interval, scan_window):
        """Function defined in GapInterface."""
        warnings.warn('TODO')
        return False

    def ble_connect(self, session_id, max_attempt=2):
        """Function defined in GapInterface."""
        bdaddr = self._ble_sessions_get_bdaddr_from_session_id(session_id)
        if bdaddr is not None:
            while max_attempt > 0:
                command = 'OPEN'
                args = [Melody._convert_standard_address_to_melody(bdaddr.addr), 'BLE']
                if bdaddr.addr_type == BleInterface.LE_BDADDR_TYPE_PRIVATE:
                    args.append(1)
                if self._execute(command, args, success_string='PENDING') is BC127_RESULT_SUCCESS:
                    if self.ble_wait_for_connection():
                        return True
                warnings.warn('ble_connect failed.')
                max_attempt -= 1
        return False

    def ble_wait_for_connection(self, timeout=10):
        """Function defined in GapInterface."""
        regex = r"OPEN_OK (\d4) BLE (\w{12})" + BC127_EOL
        response = self._serial.serial_search_regex(regex, timeout)
        if response:
            link_id = int(response[0], 16)
            bdaddr = BleInterface.Bdaddr(self._convert_melody_address_to_standard(
                response[1]), BleInterface.LE_BDADDR_TYPE_UNKNOWN)
            session_id = self._ble_sessions_get_session_from_bdaddr(bdaddr)
            if session_id:
                # virtual BLE session already exists
                self._ble_sessions_set_session_link_id(session_id, link_id)
            else:
                # need to create a new virtual BLE session
                new_session = self.ble_create_session(bdaddr)
                self._ble_sessions_set_session_link_id(new_session.session_id, link_id)
            return True
        return False

    def ble_disconnect(self, session_id):
        """Function defined in GapInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        if link_id is not None:
            command = 'CLOSE'
            args = ['{:X}'.format(link_id)]
            if self._execute(command, args) is BC127_RESULT_SUCCESS:
                return self.ble_wait_for_disconnection(session_id)
        return False

    def ble_wait_for_disconnection(self, session_id, timeout=5):
        """Function defined in GapInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        if link_id is not None:
            regex = (r"CLOSE_OK %X BLE (\w{12})" % link_id) + BC127_EOL
            response = self._serial.serial_search_regex(regex, timeout)
            if response:
                self._ble_sessions_set_session_link_id(session_id, 0)
                return True
        return False

    def ble_is_connected(self, session_id):
        """ Function defined in GapInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        return link_id is not None and link_id != 0


    # BLE GATT interface.

    def ble_get_local_mtu_size(self):
        """Function defined in GattInterface."""
        return int(self._get_config('BLE_CONFIG')[2])

    def ble_get_exchanged_mtu_size(self, session_id):
        """Function defined in GattInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        if link_id is not None and self._execute('STATUS') is BC127_RESULT_SUCCESS:
            ble_status = self._serial.serial_search_regex(
                (r"LINK %X CONNECTED BLE (\w{12}) ([0-9]{2,3})" % link_id) + BC127_EOL)
            if ble_status:
                return int(ble_status[1])
        return None

    def ble_gatt_discover_all_primary_services(self, session_id):
        """Function defined in GattInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        if link_id is not None:
            command = 'BLE_GET_SERV'
            args = ['{:X}'.format(link_id)]
            if self._execute(command, args) is BC127_RESULT_SUCCESS:
                regex = r"BLE_SERV (\d4) (\w+) ([0-9A-F|\-]+) ([0-9A-F]{4}) ([0-9A-F]{4})" \
                         + BC127_EOL
                responses = self._serial.serial_search_regex_all(regex)
                return [BleInterface.GattService(resp[2],
                                                 True,
                                                 int(resp[3], 16),
                                                 int(resp[4], 16)) for resp in responses]
        return None

    def ble_gatt_discover_all_characteristics(self, session_id):
        """Function defined in GattInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        if link_id is not None:
            command = 'BLE_GET_CHAR'
            args = ['{:X}'.format(link_id)]
            if self._execute(command, args) is BC127_RESULT_SUCCESS:
                regex = r"BLE_CHAR (\d4) (\w+) ([0-9A-F|\-]+) ([0-9A-F]{4}) ([0-9A-F]{2})" \
                         + BC127_EOL
                responses = self._serial.serial_search_regex_all(regex)
                return [BleInterface.GattCharacteristic(resp[2],
                                                        int(resp[3], 16),
                                                        int(resp[4], 16)) for resp in responses]
        return None

    def ble_gatt_add_primary_service(self, serv_uuid):
        """Function defined in GattInterface."""
        warnings.warn('TODO')
        return False

    def ble_gatt_add_characteristic(self,
                                    char_uuid,
                                    properties,
                                    permissions,
                                    max_attribute_length=0,
                                    variable_length=1,
                                    attribute_value=None):
        """Function defined in GattInterface."""
        warnings.warn('TODO')
        return False

    def ble_gatt_add_characteristic_descriptor(self,
                                               char_desc_uuid,
                                               permissions,
                                               max_attribute_length=0,
                                               variable_length=1,
                                               attribute_value=None):
        """Function defined in GattInterface."""
        warnings.warn('TODO')
        return False

    def ble_gatt_read_request(self, session_id, handle):
        """Function defined in GattInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        command = 'BLE_READ'
        args = ['{:X}'.format(link_id), '{:04X}'.format(handle)]
        return self._execute(command, args, success_string='PENDING') is BC127_RESULT_SUCCESS

    def ble_gatt_wait_for_read_request(self, session_id, handle, timeout=5):
        """Function defined in GattInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        if link_id is not None:
            regex = r"BLE_READ {:X} {:04X}".format(link_id, handle) + BC127_EOL
            response = self._serial.serial_search_regex(regex, timeout)
            if response:
                return True
        return None

    def ble_gatt_read_response(self, session_id, handle, accept, value=None, offset=0):
        """Function defined in GattInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        command = 'BLE_READ_RES'
        args = ['{:X}'.format(link_id), '{:X}'.format(
            handle), '{:X}'.format(len(value))]
        if self._execute(command, args, success_string='PENDING') is BC127_RESULT_SUCCESS:
            self._send_raw_data(value)
            return True
        return False

    def ble_gatt_wait_for_read_response(self, session_id, handle, timeout=5):
        """Function defined in GattInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        if link_id is not None:
            regex = r"BLE_READ_RES {:X} {:04X} (\d+) (\d+)".format(
                link_id, handle) + BC127_EOL
            response = self._serial.serial_search_regex(regex, timeout)
            if response:
                data_iter = iter(response[1])
                value = [int(a + b, 16) for a, b in zip(data_iter, data_iter)]
                return value
        return None

    def ble_gatt_write_request(self, session_id, handle, value, need_rsp):
        """Function defined in GattInterface."""
        if need_rsp:
            # Write Request
            link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
            command = 'BLE_WRITE'
            args = ['{:X}'.format(link_id), '{:X}'.format(
                handle), '{:X}'.format(len(value))]
            if self._execute(command, args, success_string='PENDING') is BC127_RESULT_SUCCESS:
                self._send_raw_data(value)
                return True
        else:
            # Write Without Response
            warnings.warn('Write Without Response not supported (BC127-181).')
        return False

    def ble_gatt_wait_for_write_request(self, session_id, handle, timeout=5):
        """Function defined in GattInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        if link_id is not None:
            regex = r"BLE_WRITE {:X} {:04X} (\d+) (\d+)".format(
                link_id, handle) + BC127_EOL
            response = self._serial.serial_search_regex(regex, timeout)
            if response:
                data_iter = iter(response[1])
                value = [int(a + b, 16) for a, b in zip(data_iter, data_iter)]
                return BleInterface.GattWriteReq(session_id, handle, 0, value, False)
        return None

    def ble_gatt_write_response(self, session_id, handle, accept):
        """Function defined in GattInterface."""
        warnings.warn('Write Response not supported (BC127-181).')
        return True

    def ble_gatt_wait_for_write_response(self, session_id, handle, timeout=5):
        """Function defined in GattInterface."""
        return self._serial.serial_search_line_startswith('OK', timeout)

    def ble_gatt_notification_request(self, session_id, handle, value):
        """Function defined in GattInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        command = 'BLE_NOTIFICATION'
        args = ['{:X}'.format(link_id), '{:X}'.format(
            handle), '{:X}'.format(len(value))]
        if self._execute(command, args, success_string='PENDING') is BC127_RESULT_SUCCESS:
            self._send_raw_data(value)
            return True
        return False

    def ble_gatt_wait_for_notification(self, session_id, handle, timeout=5):
        """Function defined in GattInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        if link_id is not None:
            regex = r"BLE_NOTIFICATION {:X} {:04X} (\d+) (\d+)".format(
                link_id, handle) + BC127_EOL
            response = self._serial.serial_search_regex(regex, timeout)
            if response:
                data_iter = iter(response[1])
                value = [int(a + b, 16) for a, b in zip(data_iter, data_iter)]
                return value
        return None

    def ble_gatt_indication_request(self, session_id, handle, value):
        """Function defined in GattInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        command = 'BLE_INDICATION'
        args = ['{:X}'.format(link_id), '{:X}'.format(
            handle), '{:X}'.format(len(value))]
        if self._execute(command, args, success_string='PENDING') is BC127_RESULT_SUCCESS:
            self._send_raw_data(value)
            return True
        return False

    def ble_gatt_wait_for_indication(self, session_id, handle, timeout=5):
        """Function defined in GattInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        if link_id is not None:
            regex = r"BLE_INDICATION {:X} {:04X} (\d+) (\d+)".format(
                link_id, handle) + BC127_EOL
            response = self._serial.serial_search_regex(regex, timeout)
            if response:
                data_iter = iter(response[1])
                value = [int(a + b, 16) for a, b in zip(data_iter, data_iter)]
                return value
        return None

    def ble_gatt_indication_response(self, session_id, handle):
        """Function defined in GattInterface."""
        # automatically sent by Melody
        return True

    def ble_gatt_wait_for_indication_response(self, session_id, handle, timeout=5):
        """Function defined in GattInterface."""
        return self._serial.serial_search_regex('(OK)', timeout) is not None


    # BLE BC Smart interface.

    def bc_smart_server_send_data(self, session_id, data):
        """Function defined in BcSmartInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        command = 'SEND_RAW'
        args = ['{:X}'.format(link_id), '{:X}'.format(len(data))]
        # SEND_RAW command send a Notification if notifications are enabled,
        # otherwise a Write Request if the BC Smart Data characteristic is discovered
        # on the remote device. If both fail the command return an error.
        if self._execute(command, args, success_string='PENDING') is BC127_RESULT_SUCCESS:
            self._send_raw_data(data)
            return True
        return False

    def bc_smart_server_wait_for_data(self, session_id, timeout=2):
        """Function defined in BcSmartInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        if link_id is not None:
            regex = r"RECV {:X} (\d+) (.+)".format(link_id) + BC127_EOL
            responses = self._serial.serial_search_regex_all(regex, timeout)
            if responses:
                result = []
                for resp in responses:
                    result += [ord(x) for x in resp[1]]
                return result
        return None

    def bc_smart_server_wait_for_command(self, session_id, timeout=2):
        """Function defined in BcSmartInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        if link_id is not None:
            regex = r"BC_SMART_CMD {:X} (\d+) (\w+)".format(link_id) + BC127_EOL
            response = self._serial.serial_search_regex(regex, timeout)
            if response:
                return response[1]
        return None

    def bc_smart_client_send_data(self, session_id, data):
        """Function defined in BcSmartInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        command = 'SEND_RAW'
        args = ['{:X}'.format(link_id), '{:X}'.format(len(data))]
        # SEND_RAW command send a Notification if notifications are enabled,
        # otherwise a Write Request if the BC Smart Data characteristic is discovered
        # on the remote device. If both fail the command return an error.
        if self._execute(command, args, success_string='PENDING') is BC127_RESULT_SUCCESS:
            self._send_raw_data(data)
            return True
        return False

    def bc_smart_client_wait_for_client_data(self, session_id, timeout=2):
        """Function defined in BcSmartInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        if link_id is not None:
            regex = r"RECV {:X} (\d+) (.+)".format(link_id) + BC127_EOL
            responses = self._serial.serial_search_regex_all(regex, timeout)
            if responses:
                result = []
                for resp in responses:
                    result += [ord(x) for x in resp[1]]
                return result
        return None

    def bc_smart_client_send_command(self, session_id, command):
        """Function defined in BcSmartInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        cmd = 'BC_SMART_COMMAND'
        args = ['{:X}'.format(link_id), command]
        return self._execute(cmd, args) is BC127_RESULT_SUCCESS

    def bc_smart_client_wait_for_command_response(self, session_id, timeout=5):
        """Function defined in BcSmartInterface."""
        link_id = self._ble_sessions_get_link_id_from_session_id(session_id)
        if link_id is not None:
            regex = r"BC_SMART_CMD_RESP {:X} (\d+) (\w+)".format(link_id) + BC127_EOL
            responses = self._serial.serial_search_regex_all(regex, timeout)
            if responses:
                return [resp[1] for resp in responses]
        return None
