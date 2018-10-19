#!/usr/bin/python

""" Device Manager module.

This module is used to managed the devices used by the test framework.
"""

import json


class Device:
    """Device class."""

    def __init__(self, manufacturer, model, revision, port, baud):
        self.manufacturer = manufacturer
        self.model = model
        self.revision = revision
        self.port = port
        self.baud = baud
        self._is_acquired = False

    def __eq__(self, other):
        return (self.manufacturer == other.manufacturer and self.model == other.model and
                self.revision == other.revision and
                self.port == other.port and self.baud == other.baud)

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return 'Manufacturer: ' + str(self.manufacturer) +\
            ', Model: ' + str(self.model) + ', Revision: ' + str(self.revision) +\
            ', Port: ' + self.port + ', Baud: ' + self.baud +\
            ', Acquired: ' + str(self._is_acquired)

    def is_acquired(self):
        """Returns True is the device is acquired, False otherwise."""
        return self._is_acquired

    def acquire(self):
        """Acquire device (i.e. lock)."""
        self._is_acquired = True

    def release(self):
        """Release device (i.e. unlock)."""
        self._is_acquired = False


class DeviceManager:
    """DeviceManager class."""
    def __init__(self, deviceFile):
        self.devices = []
        with open(deviceFile) as file:
            self._add_devices_from_json(json.load(file))

    def _add_devices_from_json(self, json_file):
        devices = json_file['devices']
        for dev in devices:
            self.add_device_to_list(
                Device(
                    dev['manufacturer'],
                    dev['model'],
                    dev['revision'],
                    dev['port'],
                    dev['baud']))

    def _check_if_device_registered(self, device):
        for dev in self.devices:
            if dev == device:
                return True
        return False

    def add_device_to_list(self, device):
        """Add a Device to the DeviceManager."""
        if self._check_if_device_registered(device):
            raise Exception('Device already added.')
        self.devices.append(device)

    def get_device(self, model, revision):
        """Get a Device available from the DeviceManager, for the model and revision specified."""
        for dev in self.devices:
            if not dev.is_acquired() and dev.model == model and dev.revision == revision:
                return dev
        return None
