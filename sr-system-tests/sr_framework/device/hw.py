#!/usr/bin/python

""" Hardware API.

This module contains the hardware interface (abstract class).
"""


class HWInterface:
    """ Hardware interface. """

    # [GPIO pull configuration]
    PULL_UP = 0
    PULL_DOWN = 1
    PULL_NONE = 2

    # [GPIO direction]
    GPIO_INPUT = 1
    GPIO_OUTPUT = 0

    def hw_set_uart_baudrate(self, new_baudrate):
        """ Set a new baudrate for the UART interface.

        Args:
            new_baudrate: The new baudrate.

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def hw_set_uart_flow_control(self, enable):
        """ Enable or disable flow control for the UART interface.

        Args:
            enable: True to enable flow control, otherwise false.

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def hw_get_uart_baudrate(self):
        """ Return the current UART interface baudrate.

        Returns:
            int: The current baudrate.
        """
        pass

    def hw_save_settings(self):
        """ Write the settings to non-volatile storage.

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def hw_gpio_configure(self, gpio, direction, pull_mode):
        """ Setup the parameters for a GPIO pin.

        Args:
            gpio: the GPIO to configure
            direction: 1 for input GPIO, 0 for output GPIO
            pull_mode: 0 for pull down, 1 for pull up and 2 for no pull

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def hw_gpio_read(self, gpio):
        """ Read the state of a GPIO pin.

        Args:
            gpio: the GPIO to read

        Returns:
            int: 0 for low, 1 for high, 2 for failure.
        """
        pass

    def hw_gpio_wait_for_event(self, gpio, timeout=1):
        """ Wait for a GPIO event.

        Args:
            gpio: the GPIO to wait on
            timeout: the timeout before the event shall be detected.

        Returns:
            A list of tuples of GPIOs and their new state.
        """
        pass

    def hw_gpio_write(self, gpio, value):
        """ Write to a GPIO pin.

        Args:
            gpio: the GPIO to write to
            value: 0 for low, 1 for high.

        Returns:
            bool: True for success, False otherwise.
        """
        pass
