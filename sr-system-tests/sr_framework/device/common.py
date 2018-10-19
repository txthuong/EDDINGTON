#!/usr/bin/python

""" Common API.

This module contains the common interface (abstract class).
"""


class CommonInterface:
    """ Common interface. """

    def common_send_custom_command(self, command):
        """ Send a fully custom command without any prefix.

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def common_reset(self):
        """ Reset the unit.

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def common_get_supported_command_list(self):
        """ Return the list of supported commands.

        Returns:
            list of str: List of supported commands.
        """
        pass

    def common_restore_to_defaults(self):
        """ Restore the unit to the default factory configuration.

        Returns:
            bool: True for success, False otherwise.
        """
        pass

    def common_read_manufacturer_id(self):
        """ Get manufacturer identification.

        Returns:
            str: Manufacturer identification string.
        """
        pass

    def common_read_model_id(self):
        """ Get model identification.

        Returns:
            str: Model identification string.
        """
        pass

    def common_read_revision_id(self):
        """ Get revision identification.

        Returns:
            str: Revision identification string.
        """
        pass

    def common_get_remote_controller(self):
        """ Get remote controller.

        Returns:
            int:    The session ID of the remote controller if there is
                    one, 0 otherwise.
        """
        pass

    def common_set_remote_controller(self, session_id):
        """ Set a remote controller.

        Args:
            session_id: Session ID.

        Returns:
            bool: True for success, False otherwise.
        """
        pass
