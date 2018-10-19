#!/usr/bin/python

"""This module contains the definition of the Board class object.
It is a base class for Eddington, Euler and Melody classes.
"""

from sr_framework.utils.serial_port import SerialPort
from sr_framework.utils.logger import Logger
import sr_framework.utils.helpers

class Board:
    """ Board base class."""

    def __init__(self, device):
        assert device.is_acquired() is False
        device.acquire()
        self._device = device
        self.logger = Logger(sr_framework.utils.helpers.get_valid_filename(
            self._device.port), colorise=False)
        self._serial = SerialPort(device.port, self.logger)

    def __del__(self):
        self.close_serial_port()
        self._device.release()
        self.logger.logger.handlers = []


    # DEVICE INFORMATION

    def get_device_manufacturer(self):
        """Returns the device manufacturer string."""
        return self._device.manufacturer

    def get_device_model(self):
        """Returns the device model string."""
        return self._device.model

    def get_device_revision(self):
        """Returns the device revision string."""
        return self._device.revision


    # SERIAL INTERFACE

    def open_serial_port(self):
        """ Open serial com port.

        Returns:
            bool: True for success, False otherwise.
        """
        return self._serial.serial_open(self._device.baud)

    def close_serial_port(self):
        """ Close serial com port.

        Returns:
            bool: True for success, False otherwise.
        """
        return self._serial.serial_close()

    def set_serial_baudrate(self, new_baudrate):
        """ Set a new baudrate.

        Args:
            new_baudrate: The new baudrate.

        Returns:
            bool: True for success, False otherwise.
        """
        return self._serial.serial_set_baudrate(new_baudrate)

    def get_serial_default_baudrate(self):
        """ Get initial baudrate.

        Returns:
            int: The initial baudrate.
        """
        return int(self._device.baud)


    def serial_flow_control(self, enable):
        """ Enable or disable serial flow control.

        Args:
            enable: True to enable flow control, otherwise false.

        Returns:
            bool: True for success, False otherwise.
        """
        return self._serial.serial_soft_flow_control(enable)
