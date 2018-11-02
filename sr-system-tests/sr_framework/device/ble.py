#!/usr/bin/python

""" Bluetooth Low Energy API.

This module contains the complete BLE interface (absract class).
The BLE interface itself inherits from the GAP, GATT and BC Smart interfaces.
"""
import enum


class GapInterface:
    """ Generic Access Profile (GAP) interface. """

    # [Advertising type]
    # Connectable undirected advertising
    ADV_TYPE_IND = 0
    # Connectable high duty cycle directed advertising
    ADV_TYPE_DIRECT_IND_HIGH = 1
    # Scannable undirected advertising
    ADV_TYPE_SCAN_IND = 2
    # Non connectable undirected advertising
    ADV_TYPE_NONCONN_IND = 3
    # Connectable low duty cycle directed advertising
    ADV_TYPE_DIRECT_IND_LOW = 4

    # [Advertising filter policy]
    # Process scan and connection requests from all devices.
    ADV_FP_ANY = 0
    # Process connection requests from all devices and only scan requests
    # from devices that are in the White List.
    ADV_FP_SCANREQ = 1
    # Process scan requests from all devices and only connection requests
    # from devices that are in the White List.
    ADV_FP_CONNREQ = 2
    # Process scan and connection requests only from devices in the White List.
    ADV_FP_BOTH = 3

    def ble_set_advertising_enable(self, enable, adv_data=None, scan_resp_data=None):
        """ Start or stop advertising.

        Args:
            enable:         True to start advertising, or False to stop advertising.
            adv_data:       Advertising data (e.g. [0x02, 0x01, 0x06..]).
            scan_resp_data: Scan response data (e.g. [0x05, 0x11, 0xAA, 0xBB..]).

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def ble_set_advertising_parameters(self, adv_type, adv_int_min, adv_int_max,
                                       adv_timeout, adv_fp=0):
        """ Set advertising parameters.

        Args:
            adv_type:       Advertising type (ADV_TYPE_IND, ADV_TYPE_DIRECT_IND_HIGH,
                            ADV_TYPE_SCAN_IND, ADV_TYPE_NONCONN_IND, ADV_TYPE_DIRECT_IND_LOW)
            adv_int_min:    Value in range 0x0020 to 0x4000.
            adv_int_max:    Value in range 0x0020 to 0x4000.
            adv_timeout:    Value in range 0x0000 to 0x3FFF.
            adv_fp:         Filter policy (ADV_FP_ANY, ADV_FP_SCANREQ, ADV_FP_CONNREQ,
                            ADV_FP_BOTH)

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def ble_set_peripheral_preferred_connection_parameters(self,
                                                           min_conn_interval,
                                                           max_conn_interval,
                                                           conn_latency,
                                                           supervision_timeout):
        """ Set Peripheral preferred connection parameters.

        Args:
            min_conn_interval: Value in range 0x0006 to 0x0C80.
            max_conn_interval: Value in range 0x0006 to 0x0C80.
            conn_latency: Value in range 0x0000 to 0x01F3.
            supervision_timeout: Value in range 0x000A to 0x0C80.

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    # Scan result format
    SCAN_RESULT_FORMAT_DEFAULT = 0
    SCAN_RESULT_FORMAT_RAW_DATA = 1

    class ScanResult:
        """ Scan result (parsed format). """

        def __init__(self, addr, addr_type, rssi, flag, name=None):
            self.addr = addr
            self.addr_type = addr_type
            self.rssi = rssi
            self.flag = flag
            self.name = name

        def __eq__(self, other):
            return (self.addr == other.addr and self.addr_type == other.addr_type and
                    self.rssi == other.rssi and self.flag == other.flag and self.name == other.name)

        def __ne__(self, other):
            return not self == other

        def __str__(self):
            return ('ScanResult: addr="%s", addr_type=%d, rssi=%d, flag=0x%X, name="%s"'
                    % (self.addr, self.addr_type, self.rssi, self.flag, self.name))

    class ScanRawResult:
        """ Scan result (raw format). """

        def __init__(self, addr, addr_type, rssi, raw_data):
            self.addr = addr
            self.addr_type = addr_type
            self.rssi = rssi
            self.raw_data = raw_data

        def __eq__(self, other):
            return (self.addr == other.addr and self.addr_type == other.addr_type and
                    self.rssi == other.rssi and self.raw_data == other.raw_data)

        def __ne__(self, other):
            return not self == other

        def __str__(self):
            return ('ScanRawResult: addr="%s", addr_type=%d, rssi=%d, raw data="%s"'
                    % (self.addr, self.addr_type, self.rssi,
                       ''.join('\\' + x for x in self.raw_data)))

    def ble_scan(self, duration, result_format=SCAN_RESULT_FORMAT_DEFAULT):
        """ Start scanning.

        Args:
            duration:       Duration of the scan.
            result_format:  Format of the scan results (SCAN_RESULT_FORMAT_DEFAULT
                            or SCAN_RESULT_FORMAT_RAW_DATA)

        Returns:
            List of ScanResult or ScanRawResult: List of all scan results.
        """
        pass

    def ble_set_scan_parameters(self, scan_type, scan_interval, scan_window):
        """ Set scan parameters.

        Args:
            scan_type:
                0 - Passive scanning.
                1 - Active scanning.
            scan_interval: Value in range 0x0004 to 0x4000.
            scan_window: Value in range 0x0004 to 0x4000.

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    # TMA
    def ble_get_scan_parameters(self):
        """ Get scan parameter.

        Returns:
            ScanParameter object: (scan_type, scan_interval, scan_window)
        """
        pass

    # TMA
    class ScanParameter:
        """ Scan parameter. """

        def __init__(self, scan_type, scan_interval, scan_window):
            self.scan_type = scan_type
            self.scan_interval = scan_interval
            self.scan_window = scan_window

        def __eq__(self, other):
            return (self.scan_type == other.scan_type and self.scan_interval == other.scan_interval
                    and self.scan_window == other.scan_window)

        def __ne__(self, other):
            return not self == other

        def __str__(self):
            return ('ScanParameter: scan_type="%s", scan_interval=%d, scan_window=%d'
                    % (self.scan_type, self.scan_interval, self.scan_window))

    def ble_connect(self, session_id, max_attempt=2):
        """ Connect a BLE session.

        Args:
            session_id: BLE session ID.
            max_attempt: Maximum connection attempt.

        Returns:
            bool: True if the connection is successfully established, False otherwise.
        """
        pass

    def ble_wait_for_connection(self, timeout=10):
        """ Wait for a connection establishement.

        Args:
            timeout: Timeout in seconds.

        Returns:
            bool: True if the connection is successfully established, False otherwise.
        """
        pass

    def ble_disconnect(self, session_id):
        """ Disconnect a BLE session.

        Args:
            session_id: BLE session ID.

        Returns:
            bool: True if the connection is successfully terminated, False otherwise.
        """
        pass

    def ble_wait_for_disconnection(self, session_id, timeout=5):
        """ Wait for a disconnection.

        Args:
            session_id: BLE session ID.
            timeout: Timeout in seconds.

        Returns:
            bool: True if the connection is successfully terminated, False otherwise.
        """
        pass

    def ble_is_connected(self, session_id):
        """ Check if the device is connected.

        Args:
            session_id: BLE session ID.

        Returns:
            bool: True if connected, False otherwise.
        """
        pass


class GattInterface:
    """ Generic Attribute Profile (GATT) interface. """

    class GattCharProperties(enum.IntFlag):
        """	Characteristic Properties """
        BROADCAST = 0x01
        READ = 0x02
        WRITE_WITHOUT_RESPONSE = 0x04
        WRITE = 0x08
        NOTIFY = 0x10
        INDICATE = 0x20
        AUTHENTICATED_SIGNED_WRITES = 0x40
        EXTENDED_PROPERTIES = 0x80

    class AttPermissions(enum.IntFlag):
        """	Attribute permissions """
        READ = 0x0001
        READ_ENCRYPTED = 0x0002
        READ_ENCRYPTED_MITM = 0x0004
        READ_AUTHORIZATION = 0x0008
        WRITE = 0x0010
        WRITE_ENCRYPTED = 0x0020
        WRITE_ENCRYPTED_MITM = 0x0040
        WRITE_AUTHORIZATION = 0x0080
        WRITE_SIGNED = 0x0100
        WRITE_SIGNED_MITM = 0x0200

    # -------------------------------------------
    # GATT MTU Exchange
    # -------------------------------------------
    def ble_get_local_mtu_size(self):
        """ Return the local MTU size.

        Returns:
            int: MTU size.
        """
        pass

    def ble_get_exchanged_mtu_size(self, session_id):
        """ Return the MTU size negotiated for a specific connection.

        Args:
            session_id: BLE session ID.

        Returns:
            int: MTU size.
        """
        pass

    # -------------------------------------------
    # GATT Service and Characteristic Discovery
    # -------------------------------------------
    class GattService:
        """ GATT Service. """

        def __init__(self, uuid, is_primary, start_handle, end_handle):
            """ GATT Service constructor.

            Args:
                handle:         Service handle.
                is_primary:     True for a primary service, False otherwise.
                start_handle:   Handle of the service.
                end_handle:     End handle of the service.
            """
            self.uuid = uuid
            self.is_primary = is_primary
            self.start_handle = start_handle
            self.end_handle = end_handle

        def __eq__(self, other):
            return (self.uuid == other.uuid and self.is_primary == other.is_primary and
                    self.start_handle == other.start_handle and self.end_handle == other.end_handle)

        def __ne__(self, other):
            return not self == other

        def __str__(self):
            return ('GattService: uuid=%s, is_primary=%d, start_handle=%04X, end_handle=%04X'
                    % (self.uuid, self.is_primary, self.start_handle, self.end_handle))

    class GattCharacteristic:
        """ GATT Characteristic. """

        def __init__(self, uuid, handle, properties):
            """ GATT Characteristic constructor.

            Args:
                handle:                 Characteristic handle.
                uuid:                   UUID of the characteristic descriptor.
                                        String with the following format: 'ABCD',
                                        '569A1101-B87F-490C-92CB-11BA5EA5167C').
                properties:             Bit field of characteristic properties (GattCharProperties).
            """
            self.uuid = uuid
            self.handle = handle
            self.properties = properties

        def __eq__(self, other):
            return (self.uuid == other.uuid and self.handle == other.handle
                    and self.properties == other.properties)

        def __ne__(self, other):
            return not self == other

        def __str__(self):
            return ('GattCharacteristic: uuid=%s, handle=%04X, properties=%02X'
                    % (self.uuid, self.handle, self.properties))

    def ble_gatt_discover_all_primary_services(self, session_id):
        """ [CLIENT] Discover all primary services.

        Args:
            session_id: BLE session ID.

        Returns:
            List of GattService: The list of all primary services discovered.
        """
        pass

    def ble_gatt_discover_all_characteristics(self, session_id):
        """ [CLIENT] Discover all characteristics.

        Args:
            session_id: BLE session ID.

        Returns:
            List of GattCharacteristic: The list of all characteristics discovered.
        """
        pass

    # -------------------------------------------
    # GATT Custom Database
    # -------------------------------------------
    def ble_gatt_add_service(self, serv_uuid, is_primary):
        """ [SERVER] Add a service.

        Args:
            serv_uuid:  UUID of the service.
                        String with the following format: 'ABCD',
                        '569A1101-B87F-490C-92CB-11BA5EA5167C').
            is_primary: 1 - primary service
                        0 - secondary service

        Returns:
            bool:   True if the service has been staged successfully
                    False otherwise.
        """
        pass

    def ble_gatt_add_characteristic(self,
                                    char_uuid,
                                    properties,
                                    permissions,
                                    max_attribute_length=0,
                                    variable_length=1,
                                    attribute_value=None):
        """ [SERVER] Add a characteristic to a service.

        Args:
            char_uuid:              UUID of the characteristic.
                                    String with the following format:
                                    'ABCD', '569A1101-B87F-490C-92CB-
                                    11BA5EA5167C').
            properties:             Bit field of characteristic
                                    properties (GattCharProperties).
            permissions:            Bit field of attribute permissions
                                    (AttPermissions).
            variable_length:        0 - Fixed length value
                                    1 - Variable length value
            max_attribute_length:   The maximum attribute length.
            attribute_value:        Attribute value (e.g.
                                    [0x31, 0x38, 0x57..]).

        Returns:
            bool:     True if the characteristic has been staged
                      successfully, False otherwise.
        """
        pass

    def ble_gatt_add_characteristic_descriptor(
            self,
            char_desc_uuid,
            permissions,
            max_attribute_length=0,
            variable_length=1,
            attribute_value=None):
        """ [SERVER] Add a descriptor to a characteristic.

        Args:
            char_desc_uuid:         UUID of the characteristic.
                                    String with the following format:
                                    'ABCD', '569A1101-B87F-490C-92CB-
                                    11BA5EA5167C').
            permissions:            Bit field of attribute permissions
                                    (AttPermissions).
            variable_length:        0 - Fixed length value
                                    1 - Variable length value
            max_attribute_length:   The maximum attribute length.
            attribute_value:        Attribute value (e.g.
                                    [0x31, 0x38, 0x57..]).

        Returns:
            bool:     True if the descriptor has been staged
                      successfully, False otherwise.
        """
        pass

    def ble_gatt_profile_setup(self, accept):
        """ [SERVER] Add all staged elements to the GATT server.

        Args:
            accept: 0 - Add all staged elements to the GATT server
                    1 - Discard all staged elements

        Returns:
            list of tuples: A tuple for each element added to the
                            GATT server which includes an error code
                            and a handle, e.g. [(0,28),(0,30),(903)].
        """
        pass

    # -------------------------------------------
    # GATT Read Request
    # -------------------------------------------
    def ble_gatt_read_request(self, session_id, handle):
        """ [CLIENT] GATT Read Characteristic Value.

        Args:
            session_id:     BLE session ID.
            handle:         Handle of the characteristic value.

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def ble_gatt_wait_for_read_request(self, session_id, handle,
                                       timeout=5):
        """ [SERVER] Wait for GATT Read Characteristic Value request.

        Args:
            session_id:     BLE session ID.
            handle:         Handle of the characteristic value.
            timeout:        Timeout in seconds.

        Returns:
            bool: True if the Read Request is received, False otherwise.
        """
        pass

    def ble_gatt_read_response(self,
                               session_id,
                               handle,
                               accept,
                               value=None,
                               offset=0):
        """ [SERVER] GATT Read Characteristic Value response.

        Args:
            session_id:     BLE session ID.
            handle:         Handle of the characteristic value.
            accept:         True or False.
            value:          Attribute value (e.g. [0x01, 0x42, 0x35..]).
                            Ignored if the Read Request is rejected.
            offset:         Attribute value offset

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def ble_gatt_wait_for_read_response(self, session_id, handle, timeout=5):
        """ [CLIENT] Wait for GATT Read Characteristic Value response.

        Args:
            session_id:     BLE session ID.
            handle:         Handle of the characteristic value.
            timeout:        Timeout in seconds.

        Returns:
            List of int: Characteristic value (e.g. [0x01, 0x42, 0x35..]).
        """
        pass

    # -------------------------------------------
    # GATT Write Request
    # -------------------------------------------
    def ble_gatt_write_request(self, session_id, handle, value, need_rsp):
        """ [CLIENT] GATT Write Characteristic Value.

        Args:
            session_id:     BLE session ID.
            handle:         Handle of the characteristic value.
            value:          Attribute value (e.g. [0x01, 0x42, 0x35..]).
            need_rsp:       True for a Write Request (with response),
                            or False for a Write Command (without response).

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    class GattWriteReq:
        """ GATT Write Request. """

        def __init__(self, session_id, handle, offset, value, need_rsp):
            self.session_id = session_id
            self.handle = handle
            self.offset = offset
            self.value = value
            self.need_rsp = need_rsp

        def __eq__(self, other):
            return (self.session_id == other.session_id and self.handle == other.handle and
                    self.offset == other.offset and self.value == other.value and
                    self.need_rsp == other.need_rsp)

        def __ne__(self, other):
            return not self == other

        def __str__(self):
            return ('GattWriteReq: session_id=%d, handle=%04X, offset=%d, value=%s, need_rsp=%d'
                    % (self.session_id, self.handle, self.offset, self.value, self.need_rsp))

    def ble_gatt_wait_for_write_request(self, session_id, handle, timeout=5):
        """ [SERVER] Wait for GATT Write Characteristic Value request.

        Args:
            session_id:     BLE session ID.
            handle:         Handle of the characteristic value.
            timeout:        Timeout in seconds.

        Returns:
            GattWriteReq: GATT Write Characteristic Value request.
        """
        pass

    def ble_gatt_write_response(self, session_id, handle, accept):
        """ [SERVER] GATT Write Characteristic Value response.

        Args:
            session_id:     BLE session ID.
            handle:         Handle of the characteristic value.
            accept:         True or False.

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def ble_gatt_wait_for_write_response(self, session_id, handle, timeout=5):
        """ [CLIENT] Wait for GATT Write Characteristic Value response.

        Args:
            session_id:     BLE session ID.
            handle:         Handle of the characteristic value.
            timeout:        Timeout in seconds.

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    # -------------------------------------------
    # GATT Notification
    # -------------------------------------------
    def ble_gatt_notification_request(self, session_id, handle, value):
        """ [SERVER] GATT Handle Value Notification.

        Args:
            session_id:     BLE session ID.
            handle:         Handle of the characteristic value.
            value:          Attribute value (e.g. [0x01, 0x42, 0x35..]).

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def ble_gatt_wait_for_notification(self, session_id, handle, timeout=5):
        """ [CLIENT] Wait for GATT Notification.

        Args:
            session_id:     BLE session ID.
            handle:         Handle of the characteristic value.
            timeout:        Timeout in seconds.

        Returns:
            List of int: Characteristic value (e.g. [0x01, 0x42, 0x35..]).
        """
        pass

    # -------------------------------------------
    # GATT Indication
    # -------------------------------------------
    def ble_gatt_indication_request(self, session_id, handle, value):
        """ [SERVER] GATT Handle Value Indication.

        Args:
            session_id:     BLE session ID.
            handle:         Handle of the characteristic value.
            value:          Attribute value (e.g. [0x01, 0x42, 0x35..]).

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def ble_gatt_wait_for_indication(self, session_id, handle, timeout=5):
        """ [CLIENT] Wait for GATT Indication.

        Args:
            session_id:     BLE session ID.
            handle:         Handle of the characteristic value.
            timeout:        Timeout in seconds.

        Returns:
            List of int: Characteristic value (e.g. [0x01, 0x42, 0x35..]).
        """
        pass

    def ble_gatt_indication_response(self, session_id, handle):
        """ [CLIENT] GATT Handle Value Confirmation.

        Args:
            session_id:     BLE session ID.
            handle:         Handle of the characteristic value.

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def ble_gatt_wait_for_indication_response(self, session_id, handle, timeout=5):
        """ [SERVER] Wait for GATT Handle Value Confirmation.

        Args:
            session_id:     BLE session ID.
            handle:         Handle of the characteristic value.
            timeout:        Timeout in seconds.

        Returns:
            bool: True for success, False otherwise.
        """
        pass


class BcSmartInterface:
    """ BC Smart profile interface. """
    BC_SMART_SERVICE_UUID = 'BC2F4CC6-AAEF-4351-9034-D66268E328F0'
    BC_SMART_CHAR_DATA_UUID = '06D1E5E7-79AD-4A71-8FAA-373789F7D93C'
    BC_SMART_CHAR_COMMAND_UUID = '818AE306-9C5B-448D-B51A-7ADD6A5D314D'

    # -------------------------------------------
    # BC Smart server
    # -------------------------------------------
    def bc_smart_server_send_data(self, session_id, data):
        """ Send data to a BC Smart client.

        Args:
            session_id:     BLE session ID.
            data:           Data to send (e.g. [0x01, 0x42, 0x35..]).

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def bc_smart_server_wait_for_data(self, session_id, timeout=2):
        """ Wait for data sent by a BC Smart client.

        Args:
            session_id:     BLE session ID.
            timeout:        Timeout in seconds.

        Returns:
            List of int: Data received (e.g. [0x01, 0x42, 0x35..]).
        """
        pass

    def bc_smart_server_wait_for_command(self, session_id, timeout=2):
        """ Wait for command sent by a BC Smart client.

        Args:
            session_id:     BLE session ID.
            timeout:        Timeout in seconds.

        Returns:
            str: Command received.
        """
        pass

    # -------------------------------------------
    # BC Smart client
    # -------------------------------------------
    def bc_smart_client_send_data(self, session_id, data):
        """ Send data to a BC Smart server.

        Args:
            session_id:     BLE session ID.
            data:           Data to send (e.g. [0x01, 0x42, 0x35..]).

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def bc_smart_client_wait_for_client_data(self, session_id, timeout=2):
        """ Wait for data sent by a BC Smart server.

        Args:
            session_id:     BLE session ID.
            timeout:        Timeout in seconds.

        Returns:
            List of int: Data received (e.g. [0x01, 0x42, 0x35..]).
        """
        pass

    def bc_smart_client_send_command(self, session_id, command):
        """ Send a command to a BC Smart server.

        Args:
            session_id:     BLE session ID.
            command:        Command to send (e.g. 'AT+FMM').

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def bc_smart_client_wait_for_command_response(self, session_id, timeout=5):
        """ Wait for command response sent by a BC Smart server.

        Args:
            session_id:     BLE session ID.
            timeout:        Timeout in seconds.

        Returns:
            List of str: Command response(s).
        """
        pass


class BleInterface(GapInterface, GattInterface, BcSmartInterface):
    """ Bluetooth Low Energy interface. """

    LE_BDADDR_TYPE_PUBLIC = 0
    LE_BDADDR_TYPE_PRIVATE = 1
    LE_BDADDR_TYPE_UNKNOWN = 2

    class Bdaddr:
        """ Bluetooth Address. """

        def __init__(self, addr, addr_type):
            """ Bluetooth Address constructor.

            Args:
                addr:       Bluetooth Address. String (e.g '20:FA:BB:00:01:80').
                addr_type:  Address type (see LE_BDADDR_TYPE).
            """
            if len(addr) != 17:
                raise ValueError('error invalid address')
            if ((addr_type != BleInterface.LE_BDADDR_TYPE_PUBLIC) and addr_type not in
                    (BleInterface.LE_BDADDR_TYPE_PUBLIC,
                     BleInterface.LE_BDADDR_TYPE_PRIVATE,
                     BleInterface.LE_BDADDR_TYPE_UNKNOWN)):
                raise ValueError('error invalid addr_type')
            self.addr = addr
            self.addr_type = addr_type

        def __eq__(self, other):
            # (self.addr_type == other.addr_type)
            # The address type is not always returned by Eddington or Melody commands..
            return self.addr == other.addr

        def __ne__(self, other):
            return not self == other

        def __str__(self):
            return 'Bdaddr: addr="%s", addr_type=%d' % (self.addr, self.addr_type)

    def ble_get_local_address(self):
        """ Get the local Bluetooth address.

        Returns:
            Bdaddr: The local Bluetooth address if successful, None otherwise.
        """
        pass

    # -------------------------------------------
    # Device Management
    # -------------------------------------------
    class BleSession:
        """ BLE session. """

        def __init__(self, session_id, bdaddr):
            """ BLE session constructor.

            Args:
                session_id: BLE session identifier (int).
                bdaddr: Bluetooth address (Bdaddr).
            """
            self.session_id = session_id
            self.bdaddr = bdaddr

        def __eq__(self, other):
            return (self.session_id == other.session_id) and (self.bdaddr == other.bdaddr)

        def __ne__(self, other):
            return not self == other

        def __str__(self):
            return ('BleSession: session_id=%d, addr="%s", type=%d' %
                    (self.session_id, self.bdaddr.addr, self.bdaddr.addr_type))

    def ble_create_session(self, bdaddr):
        """ Create a BLE session.

        Args:
            bdaddr: Bluetooth address of the remote device (Bdaddr).

        Returns:
            BLE Session: The BLE session if successful, None otherwise.
        """
        pass

    def ble_delete_session(self, session_id):
        """ Delete a BLE session.

        Args:
            session_id: BLE session ID.

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def ble_get_session_id_from_bdaddr(self, bdaddr):
        """ Get the session id of a registered device.

       Args:
            bdaddr: Bluetooth address of the remote device.

        Returns:
            int: BLE session id for success, None otherwise.
        """
        pass

    def ble_get_all_sessions(self):
        """ Get all BLE session(s).

        Returns:
            List of BLE Session: The list of all BLE sessions (BleSession).
        """
        pass
