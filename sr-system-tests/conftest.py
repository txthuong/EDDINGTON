#!/usr/bin/python

""" Example conftest.py - pytest configuration file.

Note that the dut and remote fixtures are mandatory to run the tests.

In this example, the device under test (DUT) is an Eddington board.
The remote device used for testing is a BC127 board.

The local devices configuration (COM port, baudrate etc..) is
extracted by the DeviceManager from the devices.json example file.

"""

import os
import pytest
from sr_framework import DeviceManager, Eddington, Euler, Melody

DM = DeviceManager(os.getcwd() + "\\devices.json")
DUT_MODEL = 'BX310X'
DUT_REVISION = 'BX310x.2.5.0-1'
REMOTE_MODEL = 'BX310X'
REMOTE_REVISION = 'BX310x.2.5.0-1'

def _get_class_from_model(model_string):
    """Return Object Class from model string."""
    class_dict = {
        'BC310X': Eddington,
        'BX310X': Euler,
        'BC127': Melody,
    }
    return class_dict[model_string]

def _acquire_device(model_string, revision_string):
    """Acquire a device matching the model string.
    Returns the device (Eddington, Euler or Melody object)."""
    device = DM.get_device(model_string, revision_string)
    assert device
    cls = _get_class_from_model(model_string)
    board = cls(device)
    return board

def _board_session_setup(board):
    """Generic board test setup (scope=session)."""
    assert board.open_serial_port()
    if board.common_reset() is False:
        # 2nd attempt
        assert board.common_reset()

def _board_session_teardown(board):
    """Generic board test teardown (scope=session)."""
    board.__del__()

@pytest.fixture(scope='session')
def _dut_session():
    """Dut session fixture."""
    dev = _acquire_device(DUT_MODEL, DUT_REVISION)
    _board_session_setup(dev)
    yield dev
    _board_session_teardown(dev)

@pytest.fixture(scope='session')
def _remote_session():
    """Remote session fixture."""
    dev = _acquire_device(REMOTE_MODEL, REMOTE_REVISION)
    _board_session_setup(dev)
    yield dev
    _board_session_teardown(dev)

def _board_function_setup(request, board):
    """Generic board test setup (scope=function)."""
    board.logger.info('------------------------------------------------')
    board.logger.info('module      : %s' % request.module.__name__)
    board.logger.info('function    : %s' % request.function.__name__)
    board.logger.info('description : %s' % request.function.__doc__)
    board.logger.info('------------------------------------------------')
    if board.common_reset() is False:
        # 2nd attempt
        assert board.common_reset()

def _board_function_teardown(board):
    """Generic board test teardown (scope=function)."""
    if board.common_reset() is False:
        # 2nd attempt
        assert board.common_reset()

@pytest.fixture(scope='function')
def dut(request, _dut_session):
    """Device Under Test."""
    _board_function_setup(request, _dut_session)
    yield _dut_session
    _board_function_teardown(_dut_session)

@pytest.fixture(scope='function')
def remote(request, _remote_session):
    """Remote Device."""
    _board_function_setup(request, _remote_session)
    yield _remote_session
    _board_function_teardown(_remote_session)
