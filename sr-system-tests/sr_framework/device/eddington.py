#!/usr/bin/python

""" eddington module.
It contains the Eddington class, which inherits from the Board class
and implements the common, ble and hw interfaces. """

import time
import warnings
from sr_framework.device.board import Board
from sr_framework.device.common import CommonInterface
from sr_framework.device.ble import BleInterface
from sr_framework.device.hw import HWInterface

# Eddington end of line character
EDD_EOL = '\r'

# Eddington default command timeout (in seconds)
DEFAULT_COMMAND_TIMEOUT = 10

# Eddington result codes
EDD_RESULT_SUCCESS = 0
EDD_RESULT_ERROR = 1
EDD_RESULT_CME_ERROR = 2
EDD_RESULT_TIMEOUT = 3

class Eddington(Board, CommonInterface, BleInterface, HWInterface):
    """
    Eddington Board
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

    # TMA
    @staticmethod
    def _convert_eddington_address_to_standard(addr):
        return addr.upper()

    def _get_result_from_response(self, command):
        success_string = 'OK' if command != '+RST' else 'Ready'
        cme_error_string = '+CME'
        error_string = 'ERROR'
        timeout = DEFAULT_COMMAND_TIMEOUT
        while timeout >= 0:
            if command == '&F':
                regex = r"(.)"
                if self._serial.serial_search_regex(regex):
                    return EDD_RESULT_SUCCESS
            if self._serial.serial_search_line_startswith(success_string):
                return EDD_RESULT_SUCCESS
            if self._serial.serial_search_line_startswith(error_string):
                return EDD_RESULT_ERROR
            if self._serial.serial_search_line_startswith(cme_error_string):
                return EDD_RESULT_CME_ERROR
            time.sleep(min(0.1, timeout))
            timeout -= 0.1
        return EDD_RESULT_TIMEOUT

    def _execute(self, command):
        """Execute AT command."""
        self._serial.serial_rx_clear()
        self._serial.serial_write_data('AT{}'.format(command) + EDD_EOL)
        return self._get_result_from_response(command)

    def _query(self, command):
        """Read AT command."""
        self._serial.serial_rx_clear()
        self._serial.serial_write_data('AT{}'.format(command) + '?' + EDD_EOL)
        return self._get_result_from_response(command)

    def _write(self, command, args):
        """Write AT command."""
        self._serial.serial_rx_clear()
        self._serial.serial_write_data('AT{}={}'.format(command, ','.join(
            (str(x) if x is not None else '') for x in args)) + EDD_EOL)
        return self._get_result_from_response(command)

    def _custom_command(self, command):
        """Custom command."""
        self._serial.serial_rx_clear()
        self._serial.serial_write_data(command + EDD_EOL)
        return self._get_result_from_response(command)


    # HW INTERFACE.

    def hw_set_uart_baudrate(self, new_baudrate):
        """Function defined in HWInterface. """
        command = '+IPR'
        args = [new_baudrate]
        result = self._write(command, args) is EDD_RESULT_SUCCESS
        if result:
            self.set_serial_baudrate(new_baudrate)
        return result

    def hw_set_uart_flow_control(self, enable):
        """Function defined in HWInterface. """
        command = '&K=3' if enable else '&K=0'
        result = self._execute(command) is EDD_RESULT_SUCCESS
        if result:
            result = self.serial_flow_control(enable)
        return result

    def hw_get_uart_baudrate(self):
        """Function defined in HWInterface. """
        command = '+IPR'
        if self._query(command) is EDD_RESULT_SUCCESS:
            regex = r"\+IPR: (\d+)"
            response = self._serial.serial_search_regex(regex)
            return int(response[0])
        return None

    def hw_save_settings(self):
        """Function defined in HWInterface. """
        command = '&W'
        return self._execute(command) is EDD_RESULT_SUCCESS

    def hw_gpio_configure(self, gpio, direction, pull_mode):
        """Function defined in HWInterface. """
        command = '+KGPIOCFG'
        args = [gpio, direction, pull_mode]
        return self._write(command, args) is EDD_RESULT_SUCCESS

    def hw_gpio_write(self, gpio, value):
        """Function defined in HWInterface. """
        if (value > 1) or (value < 0):
            return False
        command = '+KGPIO'
        args = [gpio, value]
        return self._write(command, args) is EDD_RESULT_SUCCESS

    def hw_gpio_read(self, gpio):
        """Function defined in HWInterface. """
        command = '+KGPIO'
        args = [gpio, 2]
        if self._write(command, args) is EDD_RESULT_SUCCESS:
            regex = r"\+KGPIOCFG: (\d+), ([0|1])"
            return int(self._serial.serial_search_regex(regex)[1])
        return 2

    def hw_gpio_wait_for_event(self, gpio, timeout=1):
        """Function defined in HWInterface. """
        regex = r"\+KGPIO: (\d+), (\d)"
        result = self._serial.serial_search_regex_all(regex, timeout)
        gpio_list = []
        for res in result:
            gpio_list.append((int(res[0]), int(res[1])))
        return gpio_list

    # COMMON INTERFACE.

    def common_send_custom_command(self, command):
        """Function defined in CommonInterface. """
        return self._custom_command(command) is EDD_RESULT_SUCCESS

    def common_reset(self):
        """Function defined in CommonInterface. """
        command = '+RST'
        return self._execute(command) is EDD_RESULT_SUCCESS

    def common_get_supported_command_list(self):
        """Function defined in CommonInterface. """
        command = '+CLAC'
        if self._execute(command) is EDD_RESULT_SUCCESS:
            return self._serial.serial_search_regex_all(r"(AT\+[\w]+)")
        return None

    def common_restore_to_defaults(self):
        """Function defined in CommonInterface. """
        # TODO: Clear pairing list
        command = '&F'
        return self._execute(command) is EDD_RESULT_SUCCESS

    def common_read_manufacturer_id(self):
        """Function defined in CommonInterface. """
        command = '+FMI'
        if self._execute(command) is EDD_RESULT_SUCCESS:
            regex = r"([\w| ]+)"
            return self._serial.serial_search_regex(regex)[0]
        return None

    def common_read_model_id(self):
        """Function defined in CommonInterface. """
        command = '+FMM'
        if self._execute(command) is EDD_RESULT_SUCCESS:
            regex = r"([\w]+)"
            return self._serial.serial_search_regex(regex)[0]
        return None

    def common_read_revision_id(self):
        """Function defined in CommonInterface. """
        command = '+FMR'
        if self._execute(command) is EDD_RESULT_SUCCESS:
            regex = r"([\S]+)"
            return self._serial.serial_search_regex(regex)[0]
        return None

    def common_read_bt_mac(self):
        """Function defined in CommonInterface. """
        command = '+MACADDR'
        if self._query(command) is EDD_RESULT_SUCCESS:
            regex = r"\+MACADDR: ([\w|:]{17})"
            return self._serial.serial_search_regex(regex)[0]
        return None

    def common_read_fsn(self):
        """Function defined in CommonInterface. """
        command = '+CGSN'
        if self._execute(command) is EDD_RESULT_SUCCESS:
            regex = r"(\d[A-Z]\d{12})"
            return self._serial.serial_search_regex(regex)[0]
        return None

    def common_get_remote_controller(self):
        """Function defined in CommonInterface. """
        command = '+SRREMCTRL'
        if self._query(command) is EDD_RESULT_SUCCESS:
            regex = r"\+SRREMCTRL: (\d+)"
            response = self._serial.serial_search_regex(regex)
            return int(response[0])
        return None

    def common_set_remote_controller(self, session_id):
        """Function defined in CommonInterface. """
        command = '+SRREMCTRL'
        args = [session_id]
        return self._write(command, args) is EDD_RESULT_SUCCESS


    # BLE INTERFACE.

    def ble_get_local_address(self):
        """Function defined in BleInterface. """
        command = '+SRBLEADDR'
        if self._query(command) is EDD_RESULT_SUCCESS:
            regex = r"\+SRBLEADDR: \"([\w|:]{17})\",(\d)"
            response = self._serial.serial_search_regex(regex)
            return BleInterface.Bdaddr(response[0], int(response[1]))
        return None

    def ble_create_session(self, bdaddr):
        """Function defined in BleInterface. """
        command = '+SRBLECFG'
        args = ['"' + bdaddr.addr + '"']
        if self._write(command, args) is EDD_RESULT_SUCCESS:
            regex = r"\+SRBLECFG: (\d+),([0|1]),\"([\w|:]{17})\"(,(\d),(\d+))?"
            response = self._serial.serial_search_regex(regex)
            return BleInterface.BleSession(int(response[0]),
                                           BleInterface.Bdaddr(response[2], bdaddr.addr_type))
        return None

    def ble_delete_session(self, session_id):
        """Function defined in BleInterface. """
        command = '+SRBLEDEL'
        args = [session_id]
        return self._write(command, args) is EDD_RESULT_SUCCESS

    def ble_get_session_id_from_bdaddr(self, bdaddr):
        """Function defined in BleInterface. """
        command = '+SRBLECFG'
        if self._query(command) is EDD_RESULT_SUCCESS:
            regex = r"\+SRBLECFG: (\d+),([0|1]),\"([\w|:]{17})\"(,(\d),(\d+))?"
            responses = self._serial.serial_search_regex_all(regex)
            for resp in responses:
                if resp[2] == bdaddr.addr:
                    return int(resp[0])
        return None

    def ble_get_all_sessions(self):
        """Function defined in BleInterface. """
        command = '+SRBLECFG'
        if self._query(command) is EDD_RESULT_SUCCESS:
            regex = r"\+SRBLECFG: (\d+),([0|1]),\"([\w|:]{17})\"(,(\d),(\d+))?"
            responses = self._serial.serial_search_regex_all(regex)
            sessions = []
            for resp in responses:
                sessions.append(BleInterface.BleSession(int(resp[0]), BleInterface.Bdaddr(
                    resp[2], BleInterface.LE_BDADDR_TYPE_UNKNOWN)))
            return sessions
        return None


    # BLE GAP interface.

    def ble_set_advertising_enable(self, enable, adv_data=None, scan_resp_data=None):
        """Function defined in GapInterface. """
        command = '+SRBLEADV'
        args = [int(enable)]
        if adv_data:
            args.append('"' + ''.join('\\{:02X}'.format(x)
                                      for x in adv_data) + '"')
        if scan_resp_data:
            args.append('"' + ''.join('\\{:02X}'.format(x)
                                      for x in scan_resp_data) + '"')
        return self._write(command, args) is EDD_RESULT_SUCCESS

    def ble_set_advertising_parameters(self,
                                       adv_type,
                                       adv_int_min,
                                       adv_int_max,
                                       adv_timeout,
                                       adv_fp=0):
        """Function defined in GapInterface. """
        command = '+SRBLEADVPARAMS'
        warnings.warn('adv_int_max parameter ignored.')
        args = [adv_type, adv_int_min, adv_timeout]
        if adv_fp:
            args.append(adv_fp)
        return self._write(command, args) is EDD_RESULT_SUCCESS

    def ble_set_peripheral_preferred_connection_parameters(self,
                                                           min_conn_interval,
                                                           max_conn_interval,
                                                           conn_latency,
                                                           supervision_timeout):
        """Function defined in GapInterface. """
        command = '+SRBLEPPCP'
        args = [min_conn_interval, max_conn_interval,
                conn_latency, supervision_timeout]
        return self._write(command, args) is EDD_RESULT_SUCCESS

    # TMA (Note: Depend on DEFAULT_COMMAND_TIMEOUT)
    def ble_scan(self, duration, result_format=BleInterface.SCAN_RESULT_FORMAT_DEFAULT):
        """Function defined in GapInterface. """
        command = '+SRBLESCAN'
        args = [duration, int(result_format)]
        if result_format == BleInterface.SCAN_RESULT_FORMAT_DEFAULT:
            if self._write(command, args) is EDD_RESULT_SUCCESS:
                regex = r"\"([\w|:]{17})\",([0|1]),-(\d+),(\d+)(,\"(.+)\")?"
                responses = self._serial.serial_search_regex_all(regex)
                return [BleInterface.ScanResult(Eddington._convert_eddington_address_to_standard(resp[0]),
                                                int(resp[1]),
                                                int(resp[2]),
                                                int(resp[3]),
                                                resp[4])
                        for resp in responses]
        elif result_format == BleInterface.SCAN_RESULT_FORMAT_RAW_DATA:
            if self._write(command, args) is EDD_RESULT_SUCCESS:
                regex = r"\"([\w|:]{17})\",([0|1]),-(\d+),\"((\\[0-9A-F]{2})+)\""
                responses = self._serial.serial_search_regex_all(regex)
                return [BleInterface.ScanRawResult( \
                            Eddington._convert_eddington_address_to_standard(resp[0]),
                            int(resp[1]),
                            int(resp[2]),
                            Eddington._convert_escaped_string_to_data(resp[3]))
                        for resp in responses]
        else:
            raise ValueError('invalid result_format')
        return None

    # TMA
    def ble_set_scan_parameters(self, scan_type, scan_interval, scan_window):
        """Function defined in GapInterface. """
        command = '+SRBLESCANPARAMS'
        args = [scan_type, scan_interval, scan_window]
        return self._write(command, args) is EDD_RESULT_SUCCESS

    # TMA
    def ble_get_scan_parameters(self):
        """Function defined in GapInterface. """
        command = '+SRBLESCANPARAMS'
        if self._query(command) is EDD_RESULT_SUCCESS:
            regex = r"\r\n\+SRBLESCANPARAMS: (\d+),(\d+),(\d+)\r\n"
            response = self._serial.serial_search_regex(regex)
            return BleInterface.ScanParameter(int(response[0]), int(response[1]), int(response[2]))
        return None

    # TMA
    def ble_set_connection_parameters(self, session_id, conn_interval, conn_latency, supervision_timeout):
        """Function defined in GapInterface. """
        command = '+SRBLECONNPARAMS'
        args = [session_id, conn_interval, conn_latency, supervision_timeout]
        return self._write(command, args) is EDD_RESULT_SUCCESS

    # TMA
    def ble_get_connection_parameters(self):
        """Function defined in GapInterface. """
        command = '+SRBLECONNPARAMS'
        if self._query(command) is EDD_RESULT_SUCCESS:
            regex = r"\r\n\+SRBLECONNPARAMS: (\d+),(\d+),(\d+),(\d+)\r\n"
            response = self._serial.serial_search_regex(regex)
            return BleInterface.ScanParameter(int(response[0]), int(response[1]), int(response[2]), int(response[3]))
        return None

    def ble_connect(self, session_id, max_attempt=2):
        """Function defined in GapInterface. """
        warnings.warn('Not supported yet.')
        return False

    def ble_wait_for_connection(self, timeout=10):
        """Function defined in GapInterface. """
        regex = r"\+SRBLE_IND: (\d),(\d)"
        response = self._serial.serial_search_regex(regex, timeout)
        if response and int(response[1]) == 1:
            return True
        return False

    def ble_disconnect(self, session_id):
        """Function defined in GapInterface. """
        command = '+SRBLECLOSE'
        args = [session_id]
        if self._write(command, args) is EDD_RESULT_SUCCESS:
            return self.ble_wait_for_disconnection(session_id)
        return False

    def ble_wait_for_disconnection(self, session_id, timeout=5):
        """Function defined in GapInterface. """
        regex = r"\+SRBLE_IND: (%d),(0),(\d+)" % session_id
        response = self._serial.serial_search_regex(regex, timeout)
        return True if response else False

    def ble_is_connected(self, session_id):
        """Function defined in GapInterface. """
        command = '+SRBLECFG'
        if self._query(command) is EDD_RESULT_SUCCESS:
            regex = r"\+SRBLECFG: (\d+),([0|1]),\"([\w|:]{17})\"(,(\d),(\d+))?"
            responses = self._serial.serial_search_regex_all(regex)
            for resp in responses:
                if int(resp[0]) == session_id:
                    return int(resp[1])
        return None


    # BLE GATT interface.

    def ble_get_local_mtu_size(self):
        """Function defined in GattInterface. """
        command = '+SRBLE'
        if self._query(command) is EDD_RESULT_SUCCESS:
            regex = r"\+SRBLE: \"([^\r]+)\",(\d+),(\d)"
            response = self._serial.serial_search_regex(regex)
            if response:
                return int(response[1])
        return None

    def ble_get_exchanged_mtu_size(self, session_id):
        """Function defined in GattInterface. """
        command = '+SRBLECFG'
        if self._query(command) is EDD_RESULT_SUCCESS:
            regex = r"\+SRBLECFG: (\d+),([0|1]),\"([\w|:]{17})\"(,(\d),(\d+))?"
            responses = self._serial.serial_search_regex_all(regex)
            for resp in responses:
                if int(resp[0]) == session_id:
                    return int(resp[5])
        return None

    def ble_gatt_discover_all_primary_services(self, session_id):
        """Function defined in GattInterface. """
        warnings.warn('Not supported yet.')
        return False

    def ble_gatt_discover_all_characteristics(self, session_id):
        """Function defined in GattInterface. """
        warnings.warn('Not supported yet.')
        return False

    def ble_gatt_add_service(self, serv_uuid, is_primary=1):
        """Function defined in GattInterface. """
        command = '+SRBLEADDSERV'
        args = [serv_uuid,
                is_primary]
        return self._write(command, args) is EDD_RESULT_SUCCESS

    def ble_gatt_add_characteristic(self,
                                    char_uuid,
                                    properties,
                                    permissions,
                                    max_attribute_length=0,
                                    variable_length=1,
                                    attribute_value=None):
        """Function defined in GattInterface. """
        command = '+SRBLEADDCHAR'
        args = [char_uuid,
                '{:02X}'.format(properties),
                '{:02X}'.format(permissions),
                max_attribute_length,
                variable_length,
                '"' + ''.join('\\{:02X}'.format(x)
                              for x in attribute_value) + '"']
        return self._write(command, args) is EDD_RESULT_SUCCESS

    def ble_gatt_add_characteristic_descriptor(
            self,
            char_desc_uuid,
            permissions,
            max_attribute_length=0,
            variable_length=1,
            attribute_value=None):
        """Function defined in GattInterface. """
        command = '+SRBLEADDDSCR'
        args = [char_desc_uuid,
                '{:02X}'.format(permissions),
                max_attribute_length,
                variable_length,
                '"' + ''.join('\\{:02X}'.format(x)
                              for x in attribute_value) + '"']
        return self._write(command, args) is EDD_RESULT_SUCCESS

    def ble_gatt_profile_setup(self, accept):
        """Function defined in GattInterface. """
        command = '+SRBLEPROFILESETUP'
        args = [accept]
        if self._write(command, args) is EDD_RESULT_SUCCESS:
            regex = r"\+SRBLEPROFILESETUP: (\d+),?(\d+)?"
            responses = self._serial.serial_search_regex_all(regex)
            return responses
        return None

    def ble_gatt_read_request(self, session_id, handle):
        """Function defined in GattInterface. """
        warnings.warn('Not supported yet.')
        return False

    def ble_gatt_wait_for_read_request(self, session_id, handle,
                                       timeout=5):
        """Function defined in GattInterface. """
        regex = r"\+SRBLEREAD_REQ: %d,%d" % (session_id, handle)
        return\
            self._serial.serial_search_regex(regex, timeout) is not None

    def ble_gatt_read_response(self,
                               session_id,
                               handle,
                               accept,
                               value=None,
                               offset=0):
        """Function defined in GattInterface. """
        command = '+SRBLEREADRESP'
        args = [session_id, handle, '{:d}'.format(accept),]
        if accept:
            args.append('"' + ''.join('\\{:02X}'.format(x)
                                      for x in value) + '"')
            args.append(offset)
        return self._write(command, args) is EDD_RESULT_SUCCESS

    def ble_gatt_wait_for_read_response(self, session_id, handle, timeout=5):
        """Function defined in GattInterface. """
        warnings.warn('Not supported yet.')
        return False

    def ble_gatt_write_request(self, session_id, handle, value, need_rsp):
        """Function defined in GattInterface. """
        warnings.warn('Not supported yet.')
        return False

    def ble_gatt_wait_for_write_request(self, session_id, handle, timeout=5):
        """Function defined in GattInterface. """
        regex = r"\+SRBLEWRITE_(REQ|IND): %d,%d,(\d+),(\d+),\"(.+)\"" % (
            session_id, handle)
        response = self._serial.serial_search_regex(regex, timeout)
        if response:
            offset = int(response[1])
            value = Eddington._convert_escaped_string_to_data(response[3])
            need_rsp = True if response[0] == 'REQ' else False
            return BleInterface.GattWriteReq(session_id, handle, offset, value, need_rsp)
        return None

    def ble_gatt_write_response(self, session_id, handle, accept):
        """Function defined in GattInterface. """
        command = '+SRBLEWRITERESP'
        args = [session_id, handle, '{:d}'.format(accept)]
        return self._write(command, args) is EDD_RESULT_SUCCESS

    def ble_gatt_wait_for_write_response(self, session_id, handle, timeout=5):
        """Function defined in GattInterface. """
        warnings.warn('Not supported yet.')
        return False

    def ble_gatt_notification_request(self, session_id, handle, value):
        """Function defined in GattInterface. """
        command = '+SRBLENOTIFY'
        args = [session_id, handle, '"' +
                ''.join('\\{:02X}'.format(x) for x in value) + '"']
        return self._write(command, args) is EDD_RESULT_SUCCESS

    def ble_gatt_wait_for_notification(self, session_id, handle, timeout=5):
        """Function defined in GattInterface. """
        warnings.warn('Not supported.')
        return False

    def ble_gatt_indication_request(self, session_id, handle, value):
        """Function defined in GattInterface. """
        command = '+SRBLEINDICATE'
        args = [session_id, handle, '"' +
                ''.join('\\{:02X}'.format(x) for x in value) + '"']
        return self._write(command, args) is EDD_RESULT_SUCCESS

    def ble_gatt_wait_for_indication(self, session_id, handle, timeout=5):
        """Function defined in GattInterface. """
        warnings.warn('Not supported.')
        return False

    def ble_gatt_indication_response(self, session_id, handle):
        """Function defined in GattInterface. """
        # automatically sent by Eddington
        return True

    def ble_gatt_wait_for_indication_response(self, session_id, handle, timeout=5):
        """Function defined in GattInterface. """
        regex = "OK"
        return self._serial.serial_search_regex(regex, timeout) is not None


    # BLE BC Smart interface.

    def bc_smart_server_send_data(self, session_id, data):
        """Function defined in BcSmartInterface. """
        command = '+SRBCSMARTSEND'
        warnings.warn('TODO: update gatt role param (EDDINGTON-132).')
        args = [session_id, 1, '"' +
                ''.join('\\{:02X}'.format(x) for x in data) + '"']
        return self._write(command, args) is EDD_RESULT_SUCCESS

    def bc_smart_server_wait_for_data(self, session_id, timeout=2):
        """Function defined in BcSmartInterface. """
        regex = r"\+SRBCSMARTRECV: (%d),(%d),\"(.+)\"" % (session_id, 0)
        responses = self._serial.serial_search_regex_all(regex, timeout)
        if responses:
            result = []
            for resp in responses:
                result += Eddington._convert_escaped_string_to_data(resp[2])
            return result
        return None

    def bc_smart_server_wait_for_command(self, session_id, timeout=2):
        """Function defined in BcSmartInterface. """
        regex = r"\+SRREMCMD: \"(.+)\""
        response = self._serial.serial_search_regex(regex, timeout)
        if response:
            return response[0]
        return None

    def bc_smart_client_send_data(self, session_id, data):
        """Function defined in BcSmartInterface. """
        warnings.warn('Not supported.')
        return False

    def bc_smart_client_wait_for_client_data(self, session_id, timeout=2):
        """Function defined in BcSmartInterface. """
        warnings.warn('Not supported.')
        return False

    def bc_smart_client_send_command(self, session_id, command):
        """Function defined in BcSmartInterface. """
        warnings.warn('Not supported.')
        return False

    def bc_smart_client_wait_for_command_response(self, session_id, timeout=5):
        """Function defined in BcSmartInterface. """
        warnings.warn('Not supported.')
        return False
