import pytest
import time


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
    # wait for BC Smart service discovery, and client to enables BC Smart notifications.
    time.sleep(1)
    yield
    # Disconnection
    assert remote.ble_disconnect(remote_session.session_id)
    assert dut.ble_wait_for_disconnection(dut_session_id)

def test_bc_smart_server_01(dut, remote, ble_connection):
    """Verify DUT can send data, in command mode, to a BC Smart client. """
    # GIVEN
    global dut_session_id, remote_session_id
    data = [0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x21, 0x20, 0x54, 0x68, 0x69, 0x73, 0x20, 0x69, 0x73, 0x20,
            0x61, 0x20, 0x74, 0x65, 0x73]  # , 0x74, 0x2e] an error is return is data length > MTU - 3 (20)
    # WHEN
    assert dut.bc_smart_server_send_data(dut_session_id, data)
    # THEN
    data_received = remote.bc_smart_client_wait_for_client_data(remote_session_id)
    assert data_received == data


@pytest.mark.skip(reason='TODO: EDDINGTON PROFILE INIT')
def test_bc_smart_server_02(dut, remote, ble_connection):
    """Verify DUT can receive data, in command mode, from a BC Smart client. """
    # GIVEN
    global dut_session_id, remote_session_id
    data = [0x48, 0x65, 0x6c, 0x6c, 0x6f, 0x21, 0x20, 0x54, 0x68, 0x69, 0x73,
            0x20, 0x69, 0x73, 0x20, 0x61, 0x20, 0x74, 0x65, 0x73]  # , 0x74, 0x2e]
    # WHEN
    assert remote.bc_smart_client_send_data(remote_session_id, data)
    # THEN
    data_received = dut.bc_smart_server_wait_for_data(dut_session_id)
    assert data_received == data


@pytest.mark.skip(reason='TODO: EDDINGTON PROFILE INIT')
def test_bc_smart_server_05(dut, remote, ble_connection):
    """Verify DUT can receive remote commands from a BC Smart client, and send back command responses. """
    # GIVEN
    global dut_session_id, remote_session_id
    command = 'AT'
    # WHEN
    assert dut.set_remote_controller(dut_session_id) is True
    assert remote.bc_smart_client_send_command(remote_session_id, command)
    # THEN
    command_received = dut.bc_smart_server_wait_for_command(dut_session_id)
    assert command_received == command
    command_responses = remote.bc_smart_client_wait_for_command_response(remote_session_id)
    assert 'OK' in command_responses
