import pytest
import time
from sr_framework.device.hw import HWInterface


@pytest.mark.parametrize("GPIOs",[
    [14, 16, 19, 24, 25, 27, 31, 32, 34, 35, 36, 42, 43, 44, 45, 46, 47, 48, 49, 53, 54],
    pytest.param(
        [14, 16, 18, 19, 24, 25, 26, 27, 31, 32, 34, 35, 36, 42, 43, 44, 45, 46, 47, 48, 49, 53, 54],
        marks=pytest.mark.skip(
            reason='EDDINGTON: Dev board uses pins 18 and 26 for the UART'))])
def test_hw_gpio_01(dut, GPIOs):
    """ Verify DUT can configure all GPIOs as inputs simultaneously. """
    # GIVEN
    'N\A'
    # WHEN
    for id in range(0, len(GPIOs)):
        assert dut.hw_gpio_configure(GPIOs[id], HWInterface.GPIO_INPUT, HWInterface.PULL_DOWN)
    # THEN
    'N\A'


@pytest.mark.parametrize("GPIOs",[
    [14, 16, 19, 24, 25, 27, 31, 32, 34, 35, 36, 42, 43, 44, 45, 46, 47, 48, 49, 53, 54],
    pytest.param(
        [14, 16, 18, 19, 24, 25, 26, 27, 31, 32, 34, 35, 36, 42, 43, 44, 45, 46, 47, 48, 49, 53, 54],
        marks=pytest.mark.skip(
            reason='EDDINGTON: Dev board uses pins 18 and 26 for the UART'))])
def test_hw_gpio_02(dut, GPIOs):

    """ Verify DUT can configure all GPIOs as outputs simultaneously. """
    # GIVEN
    'N\A'
    # WHEN
    for id in range(0, len(GPIOs)):
        assert dut.hw_gpio_configure(GPIOs[id], HWInterface.GPIO_OUTPUT, HWInterface.PULL_NONE)
    # THEN
    'N\A'


@pytest.mark.parametrize("GPIO_in,GPIO_out",[
    pytest.param(
        18, 26,
        marks=pytest.mark.skip(
            reason='EDDINGTON: Dev board uses these pins for the UART')),
    pytest.param(
        26, 18,
        marks=pytest.mark.skip(
            reason='EDDINGTON: Dev board uses these pins for the UART')),
    (42, 19),
    (19, 42),
    (34, 43),
    (43, 34),
    (35, 36),
    (36, 35),
    (32, 44),
    (44, 32),
    (16, 31),
    (31, 16),
    (48, 45),
    (45, 48),
    (49, 53),
    (53, 49),
    pytest.param(
        46, 47,
        marks=pytest.mark.skip(
            reason='EDDINGTON: Dev board needs HW modification to make these pins GPIOs')),
    pytest.param(
        47, 46,
        marks=pytest.mark.skip(
            reason='EDDINGTON: Dev board needs HW modification to make these pins GPIOs')),
    (27, 25),
    (25, 27),
    (24, 14),
    (14, 24)])
def test_hw_gpio_03(dut, GPIO_in, GPIO_out):
    """ Verify DUT can write to an output GPIO and sense an input GPIO. """
    # GIVEN
    assert dut.hw_gpio_configure(GPIO_out, HWInterface.GPIO_OUTPUT, HWInterface.PULL_NONE)
    assert dut.hw_gpio_write(GPIO_out, 0)
    assert dut.hw_gpio_configure(GPIO_in, HWInterface.GPIO_INPUT, HWInterface.PULL_UP)
    # WHEN
    assert dut.hw_gpio_write(GPIO_out, 1)
    # THEN
    assert [item for item in dut.hw_gpio_wait_for_event(GPIO_in) if (GPIO_in, 1) == item]
    # WHEN
    assert dut.hw_gpio_write(GPIO_out, 0)
    # THEN
    assert [item for item in dut.hw_gpio_wait_for_event(GPIO_in) if (GPIO_in, 0) == item]


@pytest.mark.parametrize("GPIO_out",[
    pytest.param(18,
        marks=pytest.mark.skip(
            reason='EDDINGTON: Dev board uses these pins for the UART')),
    pytest.param(26,
        marks=pytest.mark.skip(
            reason='EDDINGTON: Dev board uses these pins for the UART')),
    14, 16, 19, 24, 25, 27, 31, 32, 34, 35, 36, 42, 43, 44, 45, 46, 47, 48, 49, 53, 54])
def test_hw_gpio_04(dut, GPIO_out):
    """ Verify DUT can write from an output GPIO and read from the same GPIO. """
    # GIVEN
    assert dut.hw_gpio_configure(GPIO_out, HWInterface.GPIO_OUTPUT, HWInterface.PULL_NONE)
    # WHEN
    assert dut.hw_gpio_write(GPIO_out, 0)
    # THEN
    assert 0 == dut.hw_gpio_read(GPIO_out)
    # WHEN
    assert dut.hw_gpio_write(GPIO_out, 1)
    # THEN
    assert 1 == dut.hw_gpio_read(GPIO_out)


@pytest.mark.parametrize("GPIO_A,GPIO_B",[
    pytest.param(
        18, 26,
        marks=pytest.mark.skip(
            reason='EDDINGTON: Dev board uses these pins for the UART')),
    pytest.param(
        26, 18,
        marks=pytest.mark.skip(
            reason='EDDINGTON: Dev board uses these pins for the UART')),
    (42, 19),
    (19, 42),
    (34, 43),
    (43, 34),
    (35, 36),
    (36, 35),
    (32, 44),
    (44, 32),
    (16, 31),
    (31, 16),
    (48, 45),
    (45, 48),
    (49, 53),
    (53, 49),
    pytest.param(
        46, 47,
        marks=pytest.mark.skip(
            reason='EDDINGTON: Dev board needs HW modification to make these pins GPIOs')),
    pytest.param(
        47, 46,
        marks=pytest.mark.skip(
            reason='EDDINGTON: Dev board needs HW modification to make these pins GPIOs')),
    (25, 27),
    (27, 25),
    pytest.param(
        14, 24,
        marks=pytest.mark.skip(
            reason='EDDINGTON: Dev board uses pin 14 for an LED, pulls are not working correctly due to that.')),
    pytest.param(
        24, 14,
        marks=pytest.mark.skip(
            reason='EDDINGTON: Dev board uses pin 14 for an LED, pulls are not working correctly due to that.'))])
def test_hw_gpio_05(dut, GPIO_A, GPIO_B):
    """ Verify DUT can set the pull mode for a GPIO pin as pull up and pull down. """
    # GIVEN
    assert dut.hw_gpio_configure(GPIO_B, HWInterface.GPIO_INPUT, HWInterface.PULL_UP)
    assert dut.hw_gpio_configure(GPIO_A, HWInterface.GPIO_INPUT, HWInterface.PULL_NONE)
    # WHEN
    assert dut.hw_gpio_configure(GPIO_B, HWInterface.GPIO_INPUT, HWInterface.PULL_DOWN)
    # THEN
    assert [item for item in dut.hw_gpio_wait_for_event(GPIO_A) if (GPIO_A, 1) == item]
    # WHEN
    assert dut.hw_gpio_configure(GPIO_B, HWInterface.GPIO_INPUT, HWInterface.PULL_UP)
    # THEN
    assert [item for item in dut.hw_gpio_wait_for_event(GPIO_A) if (GPIO_A, 0) == item]


@pytest.mark.parametrize("GPIOs_in,GPIOs_out",[
    ([42], [19]),
    ([19], [42]),
    ([42, 34], [19, 43]),
    ([19, 43], [42, 34]),
    ([42, 34, 35], [19, 43, 36]),
    ([19, 43, 36], [42, 34, 35]),
    ([42, 34, 35, 32], [19, 43, 36, 44]),
    ([19, 43, 36, 44], [42, 34, 35, 32]),
    ([42, 34, 35, 32, 16], [19, 43, 36, 44, 31]),
    ([19, 43, 36, 44, 31], [42, 34, 35, 32, 16]),
    ([42, 34, 35, 32, 16, 48], [19, 43, 36, 44, 31, 45]),
    ([19, 43, 36, 44, 31, 45], [42, 34, 35, 32, 16, 48]),
    ([42, 34, 35, 32, 16, 48, 53], [19, 43, 36, 44, 31, 45, 49]),
    ([19, 43, 36, 44, 31, 45, 49], [42, 34, 35, 32, 16, 48, 53]),
    ([42, 34, 35, 32, 16, 48, 53], [19, 43, 36, 44, 31, 45, 49]),
    ([19, 43, 36, 44, 31, 45, 49], [42, 34, 35, 32, 16, 48, 53]),
    ([19, 43, 36, 44, 31, 45, 49, 25], [42, 34, 35, 32, 16, 48, 53, 27]),
    ([42, 34, 35, 32, 16, 48, 53, 27], [19, 43, 36, 44, 31, 45, 49, 25]),
    ([42, 34, 35, 32, 16, 48, 53, 27, 14], [19, 43, 36, 44, 31, 45, 49, 25, 24]),
    ([42, 34, 35, 32, 16, 48, 53, 27, 14], [19, 43, 36, 44, 31, 45, 49, 25, 24])])
def test_hw_gpio_06(dut, GPIOs_in, GPIOs_out):
    """ Verify DUT can write to multiple output GPIOs and sense multiple input GPIOs. """
    # GIVEN
    for id in range(0, len(GPIOs_out)):
        assert dut.hw_gpio_configure(GPIOs_out[id], HWInterface.GPIO_OUTPUT, HWInterface.PULL_NONE)
        assert dut.hw_gpio_write(GPIOs_out[id], 0)
    for id in range(0, len(GPIOs_in)):
        assert dut.hw_gpio_configure(GPIOs_in[id], HWInterface.GPIO_INPUT, HWInterface.PULL_UP)
    for id in range(0, len(GPIOs_out)):
        # WHEN
        assert dut.hw_gpio_write(GPIOs_out[id], 1)
        # THEN
        assert [item for item in dut.hw_gpio_wait_for_event(GPIOs_in[id]) if (GPIOs_in[id], 1) == item]
        # WHEN
        assert dut.hw_gpio_write(GPIOs_out[id], 0)
        # THEN
        assert [item for item in dut.hw_gpio_wait_for_event(GPIOs_in[id]) if (GPIOs_in[id], 0) == item]

@pytest.mark.parametrize("GPIO_in,GPIO_out",[
    (42, 19)])
def test_hw_gpio_07(dut, GPIO_in, GPIO_out):
    """ Verify DUT can sense very low frequency input GPIO changes. """
    # GIVEN
    assert dut.hw_gpio_configure(GPIO_out, HWInterface.GPIO_OUTPUT, HWInterface.PULL_NONE)
    assert dut.hw_gpio_write(GPIO_out, 0)
    assert dut.hw_gpio_configure(GPIO_in, HWInterface.GPIO_INPUT, HWInterface.PULL_UP)
    value = False
    for i in range(0, 16):
        # WHEN
        value = not value
        assert dut.hw_gpio_write(GPIO_out, int(value))
        # THEN
        assert [item for item in dut.hw_gpio_wait_for_event(GPIO_in) if (GPIO_in, int(value)) == item]
