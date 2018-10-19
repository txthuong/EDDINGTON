#!/usr/bin/python

""" euler module.
It contains the Euler class, which inherits from the Board class
and implements the common and ble interfaces. """

import time
import warnings
from sr_framework.device.board import Board
from sr_framework.device.common import CommonInterface
from sr_framework.device.ble import BleInterface

# Euler end of line character
EUL_EOL = '\r'

# Euler default command timeout (in seconds)
DEFAULT_COMMAND_TIMEOUT = 2

# Euler result codes
EUL_RESULT_SUCCESS = 0
EUL_RESULT_ERROR = 1
EUL_RESULT_DEFAULT_ERROR = 2
EUL_RESULT_TIMEOUT = 3

EUL_BLE_GATT_SERV_HANDLE_OFFSET = 50
EUL_BLE_GATT_SERV_HANDLE_RANGE = 100


class Euler(Board, CommonInterface, BleInterface):
    """
    Euler Board
    """

    @staticmethod
    def _convert_escaped_string_to_data(escaped_string):
        """ Convert "\\00\\01\\02Hello" to [0x00, 0x01, 0x02, 0x48, 0x65, 0x6c, 0x6c, 0x6f]. """
        result = []
        i = 0
        while i < len(escaped_string):
            if escaped_string[i] == '\\':
                value = int(escaped_string[i+1:i+3], 16)
                result.append(value)
                i += 3
            else:
                result.append(ord(escaped_string[i]))
                i += 1
        return result

    @staticmethod
    def _convert_euler_address_to_standard(addr):
        return addr.upper()

    @staticmethod
    def _convert_standard_address_to_euler(addr):
        return addr.lower()

    def _get_result_from_response(self, command, timeout=DEFAULT_COMMAND_TIMEOUT):
        success_string = 'OK' if (command not in ['+RST', '&F']) else 'READY'
        error_string = '+CME ERROR'
        while timeout >= 0:
            if self._serial.serial_search_line_startswith(success_string):
                return EUL_RESULT_SUCCESS
            if self._serial.serial_search_line_startswith(error_string):
                return EUL_RESULT_ERROR
            if self._serial.serial_search_line_startswith('ERROR'):
                return EUL_RESULT_DEFAULT_ERROR
            time.sleep(min(0.1, timeout))
            timeout -= 0.1
        return EUL_RESULT_TIMEOUT

    def _execute(self, command, timeout=DEFAULT_COMMAND_TIMEOUT):
        """Execute AT command."""
        self._serial.serial_rx_clear()
        self._serial.serial_write_data('AT{}'.format(command) + EUL_EOL)
        return self._get_result_from_response(command, timeout)

    def _query(self, command, timeout=DEFAULT_COMMAND_TIMEOUT):
        """Read AT command."""
        self._serial.serial_rx_clear()
        self._serial.serial_write_data('AT{}'.format(command) + '?' + EUL_EOL)
        return self._get_result_from_response(command, timeout)

    def _write(self, command, args, timeout=DEFAULT_COMMAND_TIMEOUT):
        """Write AT command."""
        self._serial.serial_rx_clear()
        self._serial.serial_write_data('AT{}={}'.format(command, ','.join(
            (str(x) if x is not None else '') for x in args)) + EUL_EOL)
        return self._get_result_from_response(command, timeout)

    def _get_serv_handle_from_char_handle(self, char_handle):
        """Derives the service handle value from the characteristic handle value
        Service handles start at EUL_BLE_GATT_SERV_HANDLE_OFFSET(50) and every
        service is allocated EUL_BLE_GATT_SERV_HANDLE_RANGE(100) handles.
        """
        if char_handle < EUL_BLE_GATT_SERV_HANDLE_OFFSET:
            return None
        return (char_handle - EUL_BLE_GATT_SERV_HANDLE_OFFSET) // EUL_BLE_GATT_SERV_HANDLE_RANGE * \
            EUL_BLE_GATT_SERV_HANDLE_RANGE + EUL_BLE_GATT_SERV_HANDLE_OFFSET

    def _get_transfer_id_from_read_request(self, session_id, handle, timeout=5):
        """Get transfer id from the last read request notification
        """
        regex = r"\+SRBLEREAD: %d,(\d+),%d" % (session_id, handle)
        response = self._serial.serial_search_regex(regex, timeout)
        if response:
            return int(response[0])
        return None

    def _is_a_characteristic(self, session_id, handle):
        """Return True if the handle belongs to a characteristic, False otherwise
        """
        chars = self.ble_gatt_discover_all_characteristics(session_id)
        for char in chars:
            if char.handle == handle:
                return True
        return False

    def _enable_bluetooth(self):
        """Enable the bluetooth feature if necessary
        Return True if successful and false otherwise
        """
        command = '+SRBTSYSTEM'
        if self._query(command) is EUL_RESULT_SUCCESS:
            regex = r"\+SRBTSYSTEM: (1)"
            if self._serial.serial_search_regex(regex):
                return True
            return self._write('+SRBTSYSTEM', [1]) is EUL_RESULT_SUCCESS
        return False


    # COMMON INTERFACE.

    def common_reset(self):
        """Function defined in CommonInterface. """
        command = '+RST'
        return self._execute(command) is EUL_RESULT_SUCCESS

    def common_get_supported_command_list(self):
        """Function defined in CommonInterface. """
        command = '+CLAC'
        if self._execute(command) is EUL_RESULT_SUCCESS:
            regex = r"(AT\+[\w]+)"
            return self._serial.serial_search_regex_all(regex)
        return None

    def common_restore_to_defaults(self):
        """Function defined in CommonInterface. """
        command = '&F'
        # FIXME EULER-607
        # "READY" is printed before the device is actually ready.
        # Workaround: sleep for a few seconds to make sure the device is ready.
        res = self._execute(command)
        time.sleep(3)
        return res is EUL_RESULT_SUCCESS

    def common_read_manufacturer_id(self):
        """Function defined in CommonInterface. """
        command = '+FMI'
        if self._execute(command) is EUL_RESULT_SUCCESS:
            regex = r"([\w| ]+)"
            return self._serial.serial_search_regex(regex)[0]
        return None

    def common_read_model_id(self):
        """Function defined in CommonInterface. """
        command = '+FMM'
        if self._execute(command) is EUL_RESULT_SUCCESS:
            regex = r"([\w]+)"
            return self._serial.serial_search_regex(regex)[0]
        return None

    def common_read_revision_id(self):
        """Function defined in CommonInterface. """
        command = '+FMR'
        if self._execute(command) is EUL_RESULT_SUCCESS:
            regex = r"([\S]+)"
            return self._serial.serial_search_regex(regex)[0]
        return None

    def common_get_remote_controller(self):
        """Function defined in CommonInterface. """
        command = '+SRREMCTRL'
        if self._query(command) is EUL_RESULT_SUCCESS:
            regex = r"\+SRREMCTRL: (\d+)"
            response = self._serial.serial_search_regex(regex)
            return int(response[0])
        return None

    def common_set_remote_controller(self, session_id):
        """Function defined in CommonInterface. """
        command = '+SRREMCTRL'
        args = [session_id]
        return self._write(command, args) is EUL_RESULT_SUCCESS


    # BLE INTERFACE.

    def ble_get_local_address(self):
        """Function defined in BleInterface. """
        if not self._enable_bluetooth():
            return None
        command = '+SRBTADDR'
        if self._query(command) is EUL_RESULT_SUCCESS:
            regex = r"\+SRBTADDR: \"([\w|:]{17})\""
            response = self._serial.serial_search_regex(regex)
            return BleInterface.Bdaddr(Euler._convert_euler_address_to_standard(
                response[0]), BleInterface.LE_BDADDR_TYPE_PUBLIC)
        return None

    def ble_create_session(self, bdaddr):
        """Function defined in BleInterface. """
        if not self._enable_bluetooth():
            return None
        command = '+SRBLECFG'
        args = ['"' + bdaddr.addr + '"']
        if self._write(command, args) is EUL_RESULT_SUCCESS:
            regex = r"\+SRBLECFG: (\d+),([0|1]),\"(%s)\",(\d+)" % (
                Euler._convert_standard_address_to_euler(bdaddr.addr))
            response = self._serial.serial_search_regex(regex)
            return BleInterface.BleSession(
                int(response[0]), BleInterface.Bdaddr(
                    Euler._convert_euler_address_to_standard(response[2]),
                    bdaddr.addr_type))
        return None

    def ble_delete_session(self, session_id):
        """Function defined in BleInterface. """
        if not self._enable_bluetooth():
            return False
        command = '+SRBLEDEL'
        args = [session_id]
        return self._write(command, args) is EUL_RESULT_SUCCESS

    def ble_get_session_id_from_bdaddr(self, bdaddr):
        """Function defined in BleInterface. """
        if not self._enable_bluetooth():
            return None
        command = '+SRBLECFG'
        if self._query(command) is EUL_RESULT_SUCCESS:
            regex = r"\+SRBLECFG: (\d+),([0|1]),\"(%s)\",(\d+)" % (
                Euler._convert_standard_address_to_euler(bdaddr.addr))
            response = self._serial.serial_search_regex(regex)
            if response:
                return int(response[0])
        return None

    def ble_get_all_sessions(self):
        """Function defined in BleInterface. """
        if not self._enable_bluetooth():
            return None
        command = '+SRBLECFG'
        if self._query(command) is EUL_RESULT_SUCCESS:
            regex = r"\+SRBLECFG: (\d+),([0|1]),\"([\w|:]{17})\",(\d+)"
            sessions = []
            responses = self._serial.serial_search_regex_all(regex)
            for resp in responses:
                sessions.append(BleInterface.BleSession(int(resp[0]), BleInterface.Bdaddr(
                    Euler._convert_euler_address_to_standard(resp[2]),
                    BleInterface.LE_BDADDR_TYPE_UNKNOWN)))
            return sessions
        return None


    # BLE GAP interface.

    def ble_set_advertising_enable(self, enable, adv_data=None, scan_resp_data=None):
        """Function defined in GapInterface. """
        if not self._enable_bluetooth():
            return False
        command = '+SRBLEADV'
        args = [int(enable)]
        if adv_data:
            args.append('"' + ''.join('\\{:02X}'.format(x)
                                      for x in adv_data) + '"')
        if scan_resp_data:
            args.append('"' + ''.join('\\{:02X}'.format(x)
                                      for x in scan_resp_data) + '"')
        return self._write(command, args) is EUL_RESULT_SUCCESS

    def ble_set_advertising_parameters(
            self, adv_type, adv_int_min, adv_int_max, adv_timeout, adv_fp=0):
        """Function defined in GapInterface. """
        if not self._enable_bluetooth():
            return False
        command = '+SRBLEADVPARAMS'
        warnings.warn('adv_timeout parameter not supported - ignored.')
        warnings.warn('adv_fp parameter not supported - ignored.')
        args = [adv_int_min, adv_int_max, adv_type]
        return self._write(command, args) is EUL_RESULT_SUCCESS

    def ble_set_peripheral_preferred_connection_parameters(
            self, min_conn_interval, max_conn_interval, conn_latency, supervision_timeout):
        """Function defined in GapInterface. """
        warnings.warn('Not supported.')
        return False

    def ble_scan(self, duration, result_format=BleInterface.SCAN_RESULT_FORMAT_DEFAULT):
        """ Function defined in GapInterface. """
        if not self._enable_bluetooth():
            return None
        command = '+SRBLESCAN'
        args = [duration, int(result_format)]
        if result_format == BleInterface.SCAN_RESULT_FORMAT_DEFAULT:
            if self._write(command, args, duration * 2) is EUL_RESULT_SUCCESS:
                regex = r"\"([\w|:]{17})\",([0|1]),-(\d+),(\d+)(,\"(.+)\")?"
                responses = self._serial.serial_search_regex_all(regex)
                return [BleInterface.ScanResult(Euler._convert_euler_address_to_standard(resp[0]),
                                                int(resp[1]),
                                                int(resp[2]),
                                                int(resp[3]),
                                                resp[4])
                        for resp in responses]
        elif result_format == BleInterface.SCAN_RESULT_FORMAT_RAW_DATA:
            if self._write(command, args, duration * 2) is EUL_RESULT_SUCCESS:
                regex = r"\"([\w|:]{17})\",([0|1]),-(\d+),\"((\\[0-9A-F]{2})+)\""
                responses = self._serial.serial_search_regex_all(regex)
                return [BleInterface.ScanRawResult( \
                            Euler._convert_euler_address_to_standard(resp[0]),
                            int(resp[1]),
                            int(resp[2]),
                            Euler._convert_escaped_string_to_data(resp[3]))
                        for resp in responses]
        else:
            raise ValueError('invalid result_format')
        return None

    def ble_set_scan_parameters(self, scan_type, scan_interval, scan_window):
        """Function defined in GapInterface. """
        command = '+SRBLESCANPARAMS'
        if not self._enable_bluetooth():
            return False
        args = [scan_type, scan_interval, scan_window]
        return self._write(command, args) is EUL_RESULT_SUCCESS

    def ble_connect(self, session_id, max_attempt=2):
        """Function defined in GapInterface. """
        warnings.warn('TODO, ble.py API updated: max_attempt param added.')
        if not self._enable_bluetooth():
            return False
        command = '+SRBLECNX'
        args = [session_id]
        if self._write(command, args) is EUL_RESULT_SUCCESS:
            return self.ble_wait_for_connection()
        return False

    def ble_wait_for_connection(self, timeout=10):
        """Function defined in GapInterface. """
        regex = r"\+SRBLE_IND: (\d+),(\d)"
        response = self._serial.serial_search_regex(regex, timeout)
        if response and int(response[1]) == 1:
            time.sleep(0.5) # Wait to allow MTU exchange and BC smart service registration
            return True
        return False

    def ble_disconnect(self, session_id):
        """Function defined in GapInterface. """
        if not self._enable_bluetooth():
            return False
        command = '+SRBLECLOSE'
        args = [session_id]
        if self._write(command, args) is EUL_RESULT_SUCCESS:
            return self.ble_wait_for_disconnection(session_id)
        return False

    def ble_wait_for_disconnection(self, session_id, timeout=5):
        """Function defined in GapInterface. """
        regex = r"\+SRBLE_IND: (%d),(0),(\d+)" % session_id
        response = self._serial.serial_search_regex(regex, timeout)
        return True if response else False

    def ble_is_connected(self, session_id):
        """Function defined in GapInterface. """
        if not self._enable_bluetooth():
            return None
        command = '+SRBLECFG'
        if self._query(command) is EUL_RESULT_SUCCESS:
            regex = r"\+SRBLECFG: (%d),([0|1]),\"([\w|:]{17})\",(\d+)" % (session_id)
            response = self._serial.serial_search_regex(regex)
            if response:
                return int(response[1])
        return None


    # BLE GATT interface.

    def ble_get_local_mtu_size(self):
        """Function defined in GattInterface. """
        if not self._enable_bluetooth():
            return None
        command = '+SRBLE'
        if self._query(command) is EUL_RESULT_SUCCESS:
            regex = r"\+SRBLE: \"(.+)\",(\d+),(\d)"
            response = self._serial.serial_search_regex(regex)
            if response:
                return int(response[1])
        return None

    def ble_get_exchanged_mtu_size(self, session_id):
        """Function defined in GattInterface. """
        if not self._enable_bluetooth():
            return None
        command = '+SRBLECFG'
        if self._query(command) is EUL_RESULT_SUCCESS:
            regex = r"\+SRBLECFG: (%d),([0|1]),\"([\w|:]{17})\",(\d+)" % (session_id)
            response = self._serial.serial_search_regex(regex)
            if response:
                return int(response[3])
        return None

    def ble_gatt_discover_all_primary_services(self, session_id):
        """Function defined in GattInterface. """
        if not self._enable_bluetooth():
            return None
        command = '+SRBLEDISCSERV'
        args = [session_id]
        res = None
        if self._write(command, args) is EUL_RESULT_SUCCESS:
            regex = r"\+SRBLEDISCSERV: (%d),\"([0-9a-f|\-]+)\",(1),(\d+),(\d+)" % (session_id)
            responses = self._serial.serial_search_regex_all(regex)
            res = []
            for resp in responses:
                res.append(BleInterface.GattService(resp[1].upper(), True,
                                                    int(resp[3]), int(resp[4])))
            return res
        return None

    def ble_gatt_discover_all_characteristics(self, session_id):
        """Function defined in GattInterface. """
        if not self._enable_bluetooth():
            return None
        command = '+SRBLEDISCCHAR'
        args = [session_id]
        if self._write(command, args) is EUL_RESULT_SUCCESS:
            regex = r"\+SRBLEDISCCHAR: (%d),\"([0-9a-f|\-]+)\",(\d+),(\d+)" % (session_id)
            responses = self._serial.serial_search_regex_all(regex)
            res = []
            for resp in responses:
                res.append(BleInterface.GattCharacteristic(resp[1].upper(),
                                                           int(resp[3]), int(resp[2])))
            return res
        return None

    def ble_gatt_add_primary_service(self, serv_uuid):
        """Function defined in GattInterface. """
        if not self._enable_bluetooth():
            return None
        command = '+SRBLEADDSERV'
        args = [serv_uuid]
        if self._write(command, args) is EUL_RESULT_SUCCESS:
            regex = r"\+SRBLEADDSERV: (\d+)"
            response = self._serial.serial_search_regex(regex)
            if response:
                return int(response[0])
        return None

    def ble_gatt_add_characteristic(self,
                                    char_uuid,
                                    properties,
                                    permissions,
                                    max_attribute_length=0,
                                    variable_length=1,
                                    attribute_value=None):
        """Function defined in GattInterface. """
        warnings.warn('TODO, ble.py API updated.')
        # if not self._enable_bluetooth():
            # return None
        # command = '+SRBLEADDCHAR'
        # args = [serv_handle,
                # char_uuid,
                # '{}'.format(properties),
                # '{}'.format(permissions),
                # max_attribute_length,
                # len(attribute_value),
                # '"' + ''.join('\\{:02X}'.format(x)
                              # for x in attribute_value) + '"',
                # (1 if control_policy == 0 else 0)]
        # if self._write(command, args) is EUL_RESULT_SUCCESS:
            # regex = r"\+SRBLEADDCHAR: (\d+)"
            # response = self._serial.serial_search_regex(regex)
            # if response:
                # return int(response[0])
        return None

    def ble_gatt_add_characteristic_descriptor(
            self,
            char_desc_uuid,
            permissions,
            max_attribute_length=0,
            variable_length=1,
            attribute_value=None):
        """Function defined in GattInterface. """
        warnings.warn('TODO, ble.py API updated.')
        # if not self._enable_bluetooth():
            # return None
        # command = '+SRBLEADDCHARDESCR'
        # serv_handle = self._get_serv_handle_from_char_handle(char_handle)
        # if serv_handle is None:
            # return None
        # args = [serv_handle,
                # char_desc_uuid,
                # '{}'.format(permissions),
                # max_attribute_length,
                # len(attribute_value),
                # '"' + ''.join('\\{:02X}'.format(x)
                              # for x in attribute_value) + '"',
                # (1 if control_policy == 0 else 0)]
        # if self._write(command, args) is EUL_RESULT_SUCCESS:
            # regex = r"\+SRBLEADDCHARDESCR: (\d+)"
            # response = self._serial.serial_search_regex(regex)
            # if response:
                # return int(response[0])
        return None

    def ble_gatt_read_request(self, session_id, handle):
        """Function defined in GattInterface. """
        if not self._enable_bluetooth():
            return False
        command = ''
        is_char = self._is_a_characteristic(session_id, handle)
        if is_char:
            command = '+SRBLEREADCHAR'
        else:
            command = '+SRBLEREADDESC'
        args = [session_id, handle]
        res = self._write(command, args)
        # When using AT+SRBLEREADCHAR, the OK will only be printed once the response is received
        # Workaround: Assume no immediate ERROR means that the request was successful
        if res is EUL_RESULT_ERROR or res is EUL_RESULT_DEFAULT_ERROR:
            return False
        return True

    def ble_gatt_wait_for_read_request(self, session_id, handle, timeout=5):
        """Function defined in GattInterface. """
        regex = r"\+SRBLEREAD: %d,\d+,%d" % (session_id, handle)
        return self._serial.serial_search_regex(regex, timeout) is not None

    def ble_gatt_read_response(self,
                               session_id,
                               handle,
                               accept,
                               value=None,
                               offset=0):
        """Function defined in GattInterface. """
        warnings.warn('accept parameter not supported. Read request cannot be rejected.')
        if not accept:
            return False

        transfer_id = self._get_transfer_id_from_read_request(session_id, handle)
        if transfer_id is None:
            return False
        if not self._enable_bluetooth():
            return False
        command = '+SRBLEREADRESP'
        args = [session_id, transfer_id, handle]
        args.append('"' + ''.join('\\{:02X}'.format(x)
                                  for x in value) + '"')
        return self._write(command, args) is EUL_RESULT_SUCCESS

    def ble_gatt_wait_for_read_response(self, session_id, handle, timeout=5):
        """Function defined in GattInterface. """
        warnings.warn('handle parameter ignored.')
        regex = r"\+SRBLEREADCHAR: %d,\d+,\"(.*)\"" % (session_id)
        response = self._serial.serial_search_regex(regex, timeout)
        if response:
            return self._convert_escaped_string_to_data(response[0])
        return None

    def ble_gatt_write_request(self, session_id, handle, value, need_rsp):
        """Function defined in GattInterface. """
        if not self._enable_bluetooth():
            return False
        command = ''
        is_char = self._is_a_characteristic(session_id, handle)
        if is_char:
            command = '+SRBLEWRITECHAR'
            if not need_rsp:
                command = '+SRBLEWRITECHARNORSP'
        else:
            command = '+SRBLEWRITEDESC'
        args = [session_id, handle, '"' +
                ''.join('\\{:02X}'.format(x) for x in value) + '"']
        return self._write(command, args) is EUL_RESULT_SUCCESS

    def ble_gatt_wait_for_write_request(self, session_id, handle, timeout=5):
        """Function defined in GattInterface. """
        regex = r"\+SRBLEWRITE: %d,%d,\"(.+)\"" % (session_id, handle)
        response = self._serial.serial_search_regex(regex, timeout)
        if response:
            value = Euler._convert_escaped_string_to_data(response[0])
            warnings.warn('offset not supported - ignored.')
            warnings.warn(
                'need_rsp automatically handled (accepted) by Euler. \
                Write requests cannot be rejected.')
            return BleInterface.GattWriteReq(session_id, handle, 0, value, False)
        return None

    def ble_gatt_write_response(self, session_id, handle, accept):
        """Function defined in GattInterface. """
        # Automatically sent by Euler
        warnings.warn('Automatically handled (accepted) by Euler. \
            Write requests cannot be rejected.')
        return True

    def ble_gatt_wait_for_write_response(self, session_id, handle, timeout=5):
        """Function defined in GattInterface. """
        # No specific message is received here, the OK is already handled in the
        # AT+SRBLEWRITE[...] command
        warnings.warn('Write Response not supported.')
        return True

    def ble_gatt_notification_request(self, session_id, handle, value):
        """Function defined in GattInterface. """
        if not self._enable_bluetooth():
            return False
        command = '+SRBLENOTIFY'
        args = [session_id, handle, '"' +
                ''.join('\\{:02X}'.format(x) for x in value) + '"']
        return self._write(command, args) is EUL_RESULT_SUCCESS

    def ble_gatt_wait_for_notification(self, session_id, handle, timeout=5):
        """Function defined in GattInterface. """
        regex = r"\+SRBLENOTIFICATION: %d,\d+,\"(.*)\"" % (session_id)
        response = self._serial.serial_search_regex(regex, timeout)
        if response:
            return self._convert_escaped_string_to_data(response[0])
        return None

    def ble_gatt_indication_request(self, session_id, handle, value):
        """Function defined in GattInterface. """
        if not self._enable_bluetooth():
            return False
        command = '+SRBLEINDICATE'
        args = [session_id, handle, '"' +
                ''.join('\\{:02X}'.format(x) for x in value) + '"']
        return self._write(command, args) is EUL_RESULT_SUCCESS

    def ble_gatt_wait_for_indication(self, session_id, handle, timeout=5):
        """Function defined in GattInterface. """
        regex = r"\+SRBLEINDICATION: %d,\d+,\"(.*)\"" % (session_id)
        response = self._serial.serial_search_regex(regex, timeout)
        if response:
            return self._convert_escaped_string_to_data(response[0])
        return None

    def ble_gatt_indication_response(self, session_id, handle):
        """Function defined in GattInterface. """
        # automatically sent by Euler
        return True

    def ble_gatt_wait_for_indication_response(self, session_id, handle, timeout=5):
        """Function defined in GattInterface. """
        return self._serial.serial_search_regex_all('(OK)', timeout)


    # BLE BC Smart interface.

    def bc_smart_server_send_data(self, session_id, data):
        """Function defined in BcSmartInterface. """
        if not self._enable_bluetooth():
            return False
        command = '+SRBCSMARTSEND'
        args = [session_id, 1, '"' +
                ''.join('\\{:02X}'.format(x) for x in data) + '"']
        return self._write(command, args) is EUL_RESULT_SUCCESS

    def bc_smart_server_wait_for_data(self, session_id, timeout=2):
        """Function defined in BcSmartInterface. """
        regex = r"\+SRBCSMARTRECV: (%d),(1),\"(.+)\"" % (session_id)
        responses = self._serial.serial_search_regex_all(regex, timeout)
        res = []
        for resp in responses:
            res.extend(Euler._convert_escaped_string_to_data(resp[2]))
        return res

    def bc_smart_server_wait_for_command(self, session_id, timeout=2):
        """Function defined in BcSmartInterface. """
        regex = r"\+SRREMCMD: \"(.+)\""
        response = self._serial.serial_search_regex(regex, timeout)
        if response:
            return response[0]
        return None

    def bc_smart_client_send_data(self, session_id, data):
        """Function defined in BcSmartInterface. """
        if not self._enable_bluetooth():
            return False
        command = '+SRBCSMARTSEND'
        args = [session_id, 0, '"' +
                ''.join('\\{:02X}'.format(x) for x in data) + '"']
        return self._write(command, args) is EUL_RESULT_SUCCESS

    def bc_smart_client_wait_for_client_data(self, session_id, timeout=2):
        """Function defined in BcSmartInterface. """
        regex = r"\+SRBCSMARTRECV: (%d),(0),\"(.+)\"" % (session_id)
        responses = self._serial.serial_search_regex_all(regex, timeout)
        res = []
        for resp in responses:
            res.extend(Euler._convert_escaped_string_to_data(resp[2]))
        return res

    def bc_smart_client_send_command(self, session_id, command):
        """Function defined in BcSmartInterface. """
        if not self._enable_bluetooth():
            return False
        atcommand = '+SRBCSMARTCMD'
        args = [session_id, command + EUL_EOL]
        return self._write(atcommand, args) is EUL_RESULT_SUCCESS

    def bc_smart_client_wait_for_command_response(self, session_id, timeout=5):
        """Function defined in BcSmartInterface. """
        regex = r"\+SRBCSMARTRSP: (%d),\"(.+)\"" % (session_id)
        responses = self._serial.serial_search_regex_all(regex, timeout)
        res = ''
        for resp in responses:
            res += resp[1]
        if res:
            return res.split('\\0d\\0a')
        return None
