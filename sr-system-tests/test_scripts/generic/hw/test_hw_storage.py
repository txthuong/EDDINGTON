import pytest
import time


TEST_BAUDRATE_1 = 9600
TEST_BAUDRATE_2 = 115200
TEST_BAUDRATE_3 = 460800


@pytest.mark.parametrize("baudrate",[
        TEST_BAUDRATE_1,
        TEST_BAUDRATE_2,
        TEST_BAUDRATE_3
    ]
)
def test_hw_storage_01(dut, baudrate):
    """Verify DUT can save a baudrate configuration to non-volatile storage. """
    # GIVEN
    'N/A'
    # WHEN
    assert dut.hw_set_uart_baudrate(baudrate)
    assert dut.hw_save_settings()
    assert dut.common_reset()
    # THEN
    assert dut.hw_get_uart_baudrate() == baudrate
    assert dut.hw_set_uart_baudrate(dut.get_serial_default_baudrate())
    assert dut.hw_save_settings()


@pytest.mark.parametrize("baudrate",[
        TEST_BAUDRATE_1,
        TEST_BAUDRATE_2,
        TEST_BAUDRATE_3
    ]
)
def test_hw_storage_02(dut, baudrate):
    """Verify DUT can restore all settings to the factory defaults. """
    # GIVEN
    'N/A'
    # WHEN
    assert dut.hw_set_uart_baudrate(baudrate)
    assert dut.hw_save_settings()
    assert dut.common_reset()
    # THEN
    assert dut.common_restore_to_defaults()
    assert dut.set_serial_baudrate(dut.get_serial_default_baudrate())
    assert dut.hw_get_uart_baudrate() == dut.get_serial_default_baudrate()
