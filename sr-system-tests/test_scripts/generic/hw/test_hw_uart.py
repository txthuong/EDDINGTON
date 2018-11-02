import pytest


BAUDRATE_1200 = 1200
BAUDRATE_2400 = 2400
BAUDRATE_4800 = 4800
BAUDRATE_9600 = 9600
BAUDRATE_14400 = 14400
BAUDRATE_19200 = 19200
BAUDRATE_28800 = 28800
BAUDRATE_38400 = 38400
BAUDRATE_57600 = 57600
BAUDRATE_76800 = 76800
BAUDRATE_115200 = 115200
BAUDRATE_230400 = 230400
BAUDRATE_250000 = 250000
BAUDRATE_460800 = 460800
BAUDRATE_921600 = 921600
BAUDRATE_1M = 1000000


""" 1024 byte bad command acting as a data packet. """
LONG_BAD_COMMAND ='AT+SRBLE=SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR\
SRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSRSR'


""" The number of data packets sent. """
UART_RX_LOAD = 8


@pytest.fixture(scope='function')
def revert_baudrate(dut):
    # N/A
    yield
    # Reset the baudrate
    assert dut.hw_set_uart_baudrate(dut.get_serial_default_baudrate())


def test_hw_uart_01_1(dut):
    """Verify DUT can enable UART flow control at runtime. """
    # GIVEN
    'N/A'
    # WHEN
    'N/A'
    # THEN
    assert dut.hw_set_uart_flow_control(True)


def test_hw_uart_01_2(dut):
    """Verify DUT can disable UART flow control at runtime. """
    # GIVEN
    'N/A'
    # WHEN
    'N/A'
    # THEN
    assert dut.hw_set_uart_flow_control(False)


@pytest.mark.parametrize("baudrate",[
        BAUDRATE_1200,
        BAUDRATE_2400,
        BAUDRATE_4800,
        BAUDRATE_9600,
        BAUDRATE_14400,
        BAUDRATE_19200,
        BAUDRATE_28800,
        BAUDRATE_38400,
        BAUDRATE_57600,
        BAUDRATE_76800,
        BAUDRATE_115200,
        BAUDRATE_230400,
        BAUDRATE_250000
    ]
)
def test_hw_uart_02_1(revert_baudrate, dut, baudrate):
    """Verify DUT can modify the UART baudrate at runtime with flow control disabled. """
    # GIVEN
    assert dut.hw_set_uart_flow_control(False)
    # WHEN
    assert dut.hw_set_uart_baudrate(baudrate)
    # THEN
    assert dut.hw_get_uart_baudrate() == baudrate


@pytest.mark.parametrize("baudrate",[
        BAUDRATE_1200,
        BAUDRATE_2400,
        BAUDRATE_4800,
        BAUDRATE_9600,
        BAUDRATE_14400,
        BAUDRATE_19200,
        BAUDRATE_28800,
        BAUDRATE_38400,
        BAUDRATE_57600,
        BAUDRATE_76800,
        BAUDRATE_115200,
        BAUDRATE_230400,
        BAUDRATE_250000,
        BAUDRATE_460800,
        pytest.param(
            BAUDRATE_921600,
            marks=pytest.mark.skip(
                reason='EDDINGTON: Dev board virtual port does not support this rate')
            ),
        BAUDRATE_1M
    ]
)
@pytest.mark.skip(reason="EDDINGTON: wait for SR dev board as there are flow control issues with JLink")
def test_hw_uart_02_2(revert_baudrate, dut, baudrate):
    """Verify DUT can modify the UART baudrate at runtime with flow control enabled. """
    # GIVEN
    assert dut.hw_set_uart_flow_control(False)
    # WHEN
    assert dut.hw_set_uart_baudrate(baudrate)
    # THEN
    assert dut.hw_get_uart_baudrate() == baudrate


def test_hw_uart_03_1(revert_baudrate, dut):
    """Verify DUT can modify the UART baudrate multiple times during
    runtime with flow control disabled. """
    # GIVEN
    assert dut.hw_set_uart_flow_control(False)
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_57600)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_57600
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_2400)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_2400
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_4800)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_4800
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_9600)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_9600
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_14400)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_14400
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_38400)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_38400
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_19200)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_19200
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_1200)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_1200
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_28800)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_28800
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_76800)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_76800
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_115200)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_115200
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_250000)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_250000
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_230400)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_230400


@pytest.mark.skip(reason="EDDINGTON: wait for SR dev board as there are flow control issues with JLink")
def test_hw_uart_03_2(revert_baudrate, dut):
    """Verify DUT can modify the UART baudrate multiple times during
    runtime with flow control enabled. """
    # GIVEN
    assert dut.hw_set_uart_flow_control(True)
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_57600)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_57600
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_2400)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_2400
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_4800)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_4800
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_9600)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_9600
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_14400)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_14400
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_38400)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_38400
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_19200)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_19200
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_1200)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_1200
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_28800)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_28800
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_76800)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_76800
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_115200)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_115200
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_250000)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_250000
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_230400)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_230400
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_460800)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_460800
    # WHEN
    assert dut.hw_set_uart_baudrate(BAUDRATE_1M)
    # THEN
    assert dut.hw_get_uart_baudrate() == BAUDRATE_1M


@pytest.mark.parametrize("baudrate",[
        BAUDRATE_1200,
        BAUDRATE_2400,
        BAUDRATE_4800,
        BAUDRATE_9600,
        BAUDRATE_14400,
        BAUDRATE_19200,
        BAUDRATE_28800,
        BAUDRATE_38400,
        BAUDRATE_57600,
        BAUDRATE_76800,
        BAUDRATE_115200,
        BAUDRATE_230400,
        BAUDRATE_250000,
        BAUDRATE_460800,
        pytest.param(
            BAUDRATE_921600,
            marks=pytest.mark.skip(
                reason='EDDINGTON: Dev board virtual port does not support this rate')
            ),
        BAUDRATE_1M
    ]
)
@pytest.mark.skip(reason="EDDINGTON: wait for SR dev board as there are flow control issues with JLink")
def test_hw_uart_04_1(dut, revert_baudrate, baudrate):
    """Verify DUT can handle large data streams at different baudrates with flow control enabled. """
    # GIVEN
    assert dut.hw_set_uart_flow_control(True)
    # WHEN
    assert dut.hw_set_uart_baudrate(baudrate)
    # THEN
    for x in range(1, UART_RX_LOAD):
        assert not dut.common_send_custom_command(LONG_BAD_COMMAND)


@pytest.mark.parametrize("baudrate",[
        BAUDRATE_1200,
        BAUDRATE_2400,
        BAUDRATE_4800,
        BAUDRATE_9600,
        BAUDRATE_14400,
        BAUDRATE_19200,
        BAUDRATE_28800,
        BAUDRATE_38400,
        BAUDRATE_57600,
        BAUDRATE_76800,
        BAUDRATE_115200,
        BAUDRATE_230400,
        BAUDRATE_250000
    ]
)
def test_hw_uart_04_2(dut, revert_baudrate, baudrate):
    """Verify DUT can handle large data streams at different low baudrates with flow control disabled. """
    # GIVEN
    assert dut.hw_set_uart_flow_control(False)
    # WHEN
    assert dut.hw_set_uart_baudrate(baudrate)
    # THEN
    for x in range(1, UART_RX_LOAD):
        assert not dut.common_send_custom_command(LONG_BAD_COMMAND)
