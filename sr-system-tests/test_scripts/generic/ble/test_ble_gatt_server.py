import pytest
import sr_framework.utils.helpers
from sr_framework.device.ble import BleInterface
import time
import warnings

""" 
    CUSTOM GATT DATABASE
"""
# Service
CUSTOM_SERV_UUID = 'ABCD'
# Characteristic A
CUSTOM_CHAR_A_UUID = 'CCDD'
CUSTOM_CHAR_A_PROPERTIES =\
    BleInterface.GattCharProperties.READ |\
    BleInterface.GattCharProperties.WRITE |\
    BleInterface.GattCharProperties.WRITE_WITHOUT_RESPONSE
CUSTOM_CHAR_A_PERMISSION =\
    BleInterface.AttPermissions.READ |\
    BleInterface.AttPermissions.WRITE
CUSTOM_CHAR_A_MAX_LEN = 20
CUSTOM_CHAR_A_VAR_LEN = 1
CUSTOM_CHAR_A_VALUE = [0x32, 0x33, 0x35]
# Characteristic A descriptor custom
CUSTOM_CHAR_A_DESC_UUID = '9876'
CUSTOM_CHAR_A_DESC_PERMISSION =\
    BleInterface.AttPermissions.READ |\
    BleInterface.AttPermissions.WRITE
CUSTOM_CHAR_A_DESC_MAX_LEN = 2
CUSTOM_CHAR_A_DESC_VAR_LEN = 0
CUSTOM_CHAR_A_DESC_VALUE = [0x00, 0x00]
# Characteristic B
CUSTOM_CHAR_B_UUID = 'EEFF'
CUSTOM_CHAR_B_PROPERTIES =\
    BleInterface.GattCharProperties.READ |\
    BleInterface.GattCharProperties.WRITE |\
    BleInterface.GattCharProperties.WRITE_WITHOUT_RESPONSE
CUSTOM_CHAR_B_PERMISSION =\
    BleInterface.AttPermissions.READ |\
    BleInterface.AttPermissions.WRITE |\
    BleInterface.AttPermissions.WRITE_AUTHORIZATION |\
    BleInterface.AttPermissions.READ_AUTHORIZATION
CUSTOM_CHAR_B_MAX_LEN = 0
CUSTOM_CHAR_B_VAR_LEN = 1
CUSTOM_CHAR_B_VALUE = []
# Characteristic C
CUSTOM_CHAR_C_UUID = '569A1101-B87F-490C-92CB-00000000EEFF'
CUSTOM_CHAR_C_PROPERTIES =\
    BleInterface.GattCharProperties.READ |\
    BleInterface.GattCharProperties.NOTIFY |\
    BleInterface.GattCharProperties.INDICATE
CUSTOM_CHAR_C_PERMISSION =\
    BleInterface.AttPermissions.READ |\
    BleInterface.AttPermissions.WRITE |\
    BleInterface.AttPermissions.WRITE_AUTHORIZATION |\
    BleInterface.AttPermissions.READ_AUTHORIZATION
CUSTOM_CHAR_C_MAX_LEN = 0
CUSTOM_CHAR_C_VAR_LEN = 1
CUSTOM_CHAR_C_VALUE = []
CUSTOM_CHAR_C_READ_AUTH = 1
CUSTOM_CHAR_C_WRITE_AUTH = 1
# Characteristic C descriptor CCCD
CUSTOM_CHAR_C_DESC_UUID = '2902'
CUSTOM_CHAR_C_DESC_PERMISSION =\
    BleInterface.AttPermissions.READ |\
    BleInterface.AttPermissions.WRITE
CUSTOM_CHAR_C_DESC_MAX_LEN = 2
CUSTOM_CHAR_C_DESC_VAR_LEN = 0
CUSTOM_CHAR_C_DESC_VALUE = [0x00, 0x00]

@pytest.fixture(scope='function')
def custom_db(dut):
    global  char_a_handle, char_a_desc_handle, char_b_handle,\
            char_c_handle, char_c_desc_handle
    # add service
    assert dut.ble_gatt_add_service(CUSTOM_SERV_UUID, 1)
    # add characteristic A
    assert dut.ble_gatt_add_characteristic(
        CUSTOM_CHAR_A_UUID,
        CUSTOM_CHAR_A_PROPERTIES,
        CUSTOM_CHAR_A_PERMISSION,
        CUSTOM_CHAR_A_MAX_LEN,
        CUSTOM_CHAR_A_VAR_LEN,
        CUSTOM_CHAR_A_VALUE)
    # add characteristic descriptor
    assert dut.ble_gatt_add_characteristic_descriptor(
        CUSTOM_CHAR_A_DESC_UUID,
        CUSTOM_CHAR_A_DESC_PERMISSION,
        CUSTOM_CHAR_A_DESC_MAX_LEN,
        CUSTOM_CHAR_A_DESC_VAR_LEN,
        CUSTOM_CHAR_A_DESC_VALUE)
    # add characteristic B
    assert dut.ble_gatt_add_characteristic(
        CUSTOM_CHAR_B_UUID,
        CUSTOM_CHAR_B_PROPERTIES,
        CUSTOM_CHAR_B_PERMISSION,
        CUSTOM_CHAR_B_MAX_LEN,
        CUSTOM_CHAR_B_VAR_LEN,
        CUSTOM_CHAR_B_VALUE)
    # add characteristic C
    assert dut.ble_gatt_add_characteristic(
        CUSTOM_CHAR_C_UUID,
        CUSTOM_CHAR_C_PROPERTIES,
        CUSTOM_CHAR_C_PERMISSION,
        CUSTOM_CHAR_C_MAX_LEN,
        CUSTOM_CHAR_C_VAR_LEN,
        CUSTOM_CHAR_C_VALUE)
    # add characteristic descriptor
    assert dut.ble_gatt_add_characteristic_descriptor(
        CUSTOM_CHAR_C_DESC_UUID,
        CUSTOM_CHAR_C_DESC_PERMISSION,
        CUSTOM_CHAR_C_DESC_MAX_LEN,
        CUSTOM_CHAR_C_DESC_VAR_LEN,
        CUSTOM_CHAR_C_DESC_VALUE)
    # profile setup
    responses = dut.ble_gatt_profile_setup(1)
    for e in responses:
        assert 0 == int(e[0])
    # distribute handles
    char_a_handle = int(responses[1][1])
    char_a_desc_handle = int(responses[2][1])
    char_b_handle = int(responses[3][1])
    char_c_handle = int(responses[4][1])
    char_c_desc_handle = int(responses[5][1])


@pytest.fixture(scope='function')
def ble_connection(dut, remote):
    # Connection
    global dut_session_id, remote_session_id
    dut_bdaddr = dut.ble_get_local_address()
    remote_bdaddr = remote.ble_get_local_address()
    assert dut.ble_set_advertising_enable(True)
    remote_session = remote.ble_create_session(dut_bdaddr)
    assert remote.ble_connect(remote_session.session_id)
    assert dut.ble_wait_for_connection()
    dut_session_id = dut.ble_get_session_id_from_bdaddr(remote_bdaddr)
    assert dut_session_id is not None
    remote_session_id = remote_session.session_id
    yield
    # Disconnection
    assert remote.ble_disconnect(remote_session.session_id)
    assert dut.ble_wait_for_disconnection(dut_session_id)


def test_ble_gatt_server_01_1(dut, remote, ble_connection):
    """Verify DUT automatically responds to GATT Service discovery request from a remote Client. """
    # GIVEN
    global dut_session_id, remote_session_id
    # WHEN
    services = remote.ble_gatt_discover_all_primary_services(remote_session_id)
    # THEN
    assert len([s for s in services if s.uuid == '1800' and s.is_primary == True]) == 1  # GAP service
    assert len([s for s in services if s.uuid == '1801' and s.is_primary == True]) == 1  # GATT service
    assert len([s for s in services if s.uuid == BleInterface.BC_SMART_SERVICE_UUID and s.is_primary == True]) == 1  # BC Smart service


def test_ble_gatt_server_01_2(dut, remote, ble_connection):
    """Verify DUT automatically responds to GATT Characteristic discovery request from a remote Client. """
    # GIVEN
    global dut_session_id, remote_session_id
    # WHEN
    characteristics = remote.ble_gatt_discover_all_characteristics(
        remote_session_id)
    # THEN
    assert len([c for c in characteristics if c.uuid == '2A00']) == 1  # GAP device name
    assert len([c for c in characteristics if c.uuid == '2A01']) == 1  # GAP appearance
    assert len([c for c in characteristics if c.uuid == '2A05']) == 1  # GATT service changed
    assert len([c for c in characteristics if c.uuid == BleInterface.BC_SMART_CHAR_DATA_UUID]) == 1  # GATT service changed
    assert len([c for c in characteristics if c.uuid == BleInterface.BC_SMART_CHAR_COMMAND_UUID]) == 1  # GATT service changed


def test_ble_gatt_server_02(dut, remote, ble_connection):
    """Verify DUT can set the local MTU and use it to reply a MTU Exchange request from a remote Client. """
    # GIVEN
    global dut_session_id, remote_session_id
    # WHEN
    'N/A'
    # THEN
    expected_mtu = min(dut.ble_get_local_mtu_size(), remote.ble_get_local_mtu_size())
    assert dut.ble_get_exchanged_mtu_size(dut_session_id) == expected_mtu
    assert remote.ble_get_exchanged_mtu_size(remote_session_id) == expected_mtu


def test_ble_gatt_server_03_1(dut, remote, custom_db, ble_connection):
    """Verify DUT can reply to a GATT Read request from a remote Client
    by sending a GATT Read Response (Read Request handled by the
    user). """
    # GIVEN
    global dut_session_id, remote_session_id
    # WHEN
    assert remote.ble_gatt_read_request(remote_session_id,
                                        char_b_handle)
    # THEN
    assert dut.ble_gatt_wait_for_read_request(dut_session_id,
                                              char_b_handle)
    value = [0x00, 0x01, 0x02, 0x03, 0x04]
    assert dut.ble_gatt_read_response(dut_session_id,
                                      char_b_handle,
                                      True,
                                      value,
                                      0)
    assert  value ==\
            remote.ble_gatt_wait_for_read_response(remote_session_id,
                                                   char_b_handle)


def test_ble_gatt_server_03_2(dut, remote, custom_db, ble_connection):
    """Verify DUT can reject a GATT Read request from a remote Client
    by sending an Error Response (Read Request handled by the user). """
    # GIVEN
    global dut_session_id, remote_session_id
    # WHEN
    assert remote.ble_gatt_read_request(remote_session_id,
                                        char_b_handle)
    # THEN
    assert dut.ble_gatt_wait_for_read_request(dut_session_id,
                                              char_b_handle)
    assert dut.ble_gatt_read_response(dut_session_id,
                                      char_b_handle,
                                      False)
    assert remote.ble_gatt_wait_for_read_response(remote_session_id,
                                                  char_b_handle
                                                  ) is None


def test_ble_gatt_server_03_3(dut, remote, custom_db, ble_connection):
    """Verify DUT can reply to a GATT Read request from a remote Client
    by sending a GATT Read Response (Read Request automatically
    handled). """
    # GIVEN
    global dut_session_id, remote_session_id
    # WHEN
    assert remote.ble_gatt_read_request(remote_session_id,
                                        char_a_handle)
    # THEN
    assert remote.ble_gatt_wait_for_read_response(remote_session_id,
                                                  char_a_handle
                                                  ) ==\
                                                   CUSTOM_CHAR_A_VALUE


def test_ble_gatt_server_04_1(dut, remote, custom_db, ble_connection):
    """Verify DUT can reply to a GATT Write request from a remote Client
    and send GATT Write Response (Write Request handled by the
    user). """
    # GIVEN
    global dut_session_id, remote_session_id
    # WHEN
    value = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05]
    assert remote.ble_gatt_write_request(remote_session_id,
                                         char_b_handle,
                                         value,
                                         True)
    # THEN
    write_req = dut.ble_gatt_wait_for_write_request(dut_session_id,
                                                    char_b_handle)
    assert write_req.value == value
    assert write_req.need_rsp == True
    assert dut.ble_gatt_write_response(dut_session_id,
                                       char_b_handle,
                                       True)
    assert remote.ble_gatt_wait_for_write_response(remote_session_id,
                                                   char_b_handle)


def test_ble_gatt_server_04_2(dut, remote, custom_db, ble_connection):
    """Verify DUT can reject a GATT Write request from a remote Client
    by sending an Error Response (Write Request handled by the
    user). """
    # GIVEN
    global dut_session_id, remote_session_id
    # WHEN
    value = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05]
    assert remote.ble_gatt_write_request(remote_session_id,
                                         char_b_handle,
                                         value,
                                         True)
    # THEN
    write_req = dut.ble_gatt_wait_for_write_request(dut_session_id,
                                                    char_b_handle)
    assert write_req.value == value
    assert write_req.need_rsp == True
    assert dut.ble_gatt_write_response(dut_session_id,
                                       char_b_handle,
                                       False)
    assert not\
        remote.ble_gatt_wait_for_write_response(remote_session_id,
                                                char_b_handle)


def test_ble_gatt_server_04_3(dut, remote, custom_db, ble_connection):
    """Verify DUT can reply to a GATT Write request from a remote
    Client and send GATT Write Response. (Write Request automatically
    handled). """
    # GIVEN
    global dut_session_id, remote_session_id
    # WHEN
    value = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05]
    assert remote.ble_gatt_write_request(remote_session_id,
                                         char_a_handle,
                                         value,
                                         True)
    # THEN
    write_req = dut.ble_gatt_wait_for_write_request(dut_session_id,
                                                    char_a_handle)
    assert write_req.value == value
    assert write_req.need_rsp == False
    assert remote.ble_gatt_wait_for_write_response(remote_session_id,
                                                   char_a_handle)


@pytest.mark.skip(reason='TODO: BC127-181')
def test_ble_gatt_server_05(dut, remote, custom_db, ble_connection):
    """Verify DUT can receive GATT Write without response request from a remote Client. """
    # GIVEN
    global dut_session_id, remote_session_id
    # WHEN
    value = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05]
    assert remote.ble_gatt_write_request(remote_session_id, char_a_handle, value, False)
    # THEN
    write_req = dut.ble_gatt_wait_for_write_request(dut_session_id, char_a_handle)
    assert write_req.value == value
    assert write_req.need_rsp == False
    assert remote.ble_gatt_wait_for_write_response(remote_session_id, char_a_handle)


def test_ble_gatt_server_06(dut, remote, custom_db, ble_connection):
    """Verify DUT can send GATT Notifications to a remote Client. """
    # GIVEN
    global dut_session_id, remote_session_id
    assert remote.ble_gatt_write_request(remote_session_id,
                                         char_c_desc_handle,
                                         [0x01, 0x00],
                                         True)
    assert remote.ble_gatt_wait_for_write_response(remote_session_id,
                                                   char_c_desc_handle)
    # WHEN
    value = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05]
    assert dut.ble_gatt_notification_request(remote_session_id,
                                             char_c_handle,
                                             value)
    # THEN
    assert remote.ble_gatt_wait_for_notification(dut_session_id,
                                                 char_c_handle) == value


def test_ble_gatt_server_07(dut, remote, custom_db, ble_connection):
    """Verify DUT can send GATT Indications to a remote Client. """
    # GIVEN
    global dut_session_id, remote_session_id
    assert remote.ble_gatt_write_request(remote_session_id,
                                         char_c_desc_handle,
                                         [0x02, 0x00],
                                         True)
    assert remote.ble_gatt_wait_for_write_response(remote_session_id,
                                                   char_c_desc_handle)
    # WHEN
    value = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05]
    assert dut.ble_gatt_indication_request(remote_session_id,
                                           char_c_handle,
                                           value)
    # THEN
    assert remote.ble_gatt_wait_for_indication(remote_session_id,
                                               char_c_handle) == value
    assert remote.ble_gatt_indication_response(remote_session_id,
                                               char_c_handle)
    assert dut.ble_gatt_wait_for_indication_response(dut_session_id,
                                                     char_c_handle)


def test_ble_gatt_server_08(dut, remote, custom_db, ble_connection):
    """Verify DUT can set a custom GATT database (Primary services,
    characteristics and characteristic descriptors). """
    # GIVEN
    global dut_session_id, remote_session_id
    # WHEN
    'N/A'
    # THEN
    services =\
        remote.ble_gatt_discover_all_primary_services(remote_session_id)
    # Custom service
    assert\
        1 == len(
            [s for s in services
                if s.uuid == CUSTOM_SERV_UUID and s.is_primary == True
            ]
        )
    characteristics =\
        remote.ble_gatt_discover_all_characteristics(remote_session_id)
    # Custom characteristic A
    assert\
        1 == len(
            [c for c in characteristics
                if  c.uuid == CUSTOM_CHAR_A_UUID and
                    c.properties == CUSTOM_CHAR_A_PROPERTIES
            ]
        )
    # Custom characteristic B
    assert\
        1 == len(
            [c for c in characteristics
                if  c.uuid == CUSTOM_CHAR_B_UUID and
                    c.properties == CUSTOM_CHAR_B_PROPERTIES
            ]
        )
