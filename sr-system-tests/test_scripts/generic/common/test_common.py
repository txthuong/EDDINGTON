import pytest


def test_common_0001(dut):
    """ Verify command to get the list of supported AT commands. """
    list = dut.common_get_supported_command_list()
    assert len(list) > 0


def test_common_0002(dut):
    """ Verify command to reset the DUT. """
    assert dut.common_reset() is True


def test_common_0003(dut):
    """ Verify command to get the manufacturer identification. """
    assert dut.common_read_manufacturer_id() == dut.get_device_manufacturer()


def test_common_0004(dut):
    """ Verify command to get the model identification. """
    assert dut.common_read_model_id() == dut.get_device_model()


def test_common_0005(dut):
    """ Verify command to get the revision identification. """
    assert dut.common_read_revision_id() == dut.get_device_revision()
