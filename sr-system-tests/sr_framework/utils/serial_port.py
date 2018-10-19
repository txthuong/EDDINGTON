#!/usr/bin/python

""" Serial Port API.

This module contains functionalities to send/receive data over a serial port.
"""

import io
import time
import re
import threading
import binascii
import serial

class SerialPort:
    """ Generic class to serial interface.

        serial_open and serial_close shall be called to open and close the
        serial port.

        [TX] Data shall be sent to the serial interface by calling
        serial_write_data.

        [RX] Data received from the serial interface is automatically stored in
         rx_data buffer (read_serial thread).

        serial_clear clears the buffer.

        serial_search_line, serial_search_line_startswith and
        serial_search_regex can be called to retrieve a line from the buffer.

        Attributes:
            com_port (str): Serial com port.
            logger: Logger object.
    """
    def __init__(self, com_port, logger=None):
        self.com_port = com_port
        self.ser = None
        self.sio = None
        self.logger = logger
        self.rx_data = []
        self.rx_thread = None
        self.rx_lock = threading.Lock()
        self.stop_evt = threading.Event()
        self.initial_baudrate = 0

    @staticmethod
    def __read_serial_thread(com_port, sio, rx_data, lock, logger, stop_evt):
        """ Read serial thread. Appends line by line the data received
        from serial com port to serial rx buffer. """
        while not stop_evt.isSet():
            for line in sio.readlines():
                lock.acquire()
                # append to last line, which might not be complete so re-split lines in case
                new_lines = (
                    rx_data[-1] + line if rx_data else line).splitlines(True)
                del rx_data[-1:]
                rx_data += new_lines
                prefix = com_port + " < "
                lock.release()
                logger.debug_rx(prefix + line)

    def serial_read_thread_start(self):
        """ Start read serial thread. """
        if not self.rx_thread or not self.rx_thread.is_alive():
            self.stop_evt.clear()
            self.rx_thread = threading.Thread(target=SerialPort.__read_serial_thread, args=(
                self.com_port, self.sio, self.rx_data, self.rx_lock, self.logger, self.stop_evt))
            self.rx_thread.daemon = True
            self.rx_thread.start()

    def serial_read_thread_stop(self):
        """ Stop read serial thread. """
        self.stop_evt.set()

    def serial_open(self, baudrate=9600):
        """ Open serial port. """
        try:
            self.ser = serial.Serial(self.com_port, baudrate, timeout=0.1)
        except serial.SerialException:
            return False
        self.ser.flushInput()
        self.ser.flushOutput()
        self.sio = io.TextIOWrapper(io.BufferedRWPair(
            self.ser, self.ser), encoding='ascii', errors='backslashreplace', newline='\r')
        self.serial_read_thread_start()
        time.sleep(0.5)  # wait for device to be READY if reset after flashing
        return True

    def serial_close(self):
        """ Close serial port. """
        if self.ser.isOpen() is False:
            return False
        self.serial_read_thread_stop()
        self.ser.rts = False  # if this is not set to False, BX310x resets
        self.ser.close()
        return True

    def serial_rx_clear(self):
        """ Clear data in serial RX buffer. """
        for line in self.rx_data[:]:
            self.rx_lock.acquire()
            self.rx_data.remove(line)
            self.rx_lock.release()

    def serial_set_baudrate(self, new_baudrate):
        """ Set a new baudrate. """
        self.ser.baudrate = new_baudrate
        time.sleep(0.5) # Wait for the baudrate to be modified.
        return True

    def serial_soft_flow_control(self, enable):
        """ Set the flow control mode. """
        self.ser.xonxoff = enable
        time.sleep(0.5) # Wait for the flow control to be modified.
        return True

    def serial_search_line_startswith(self, prefix, timeout=0):
        """ Search for the most recent line starting with prefix in the serial rx buffer.
        Returns the complete line if found, None otherwise. """
        result = None
        while timeout >= 0:
            # search for prefix in rx_data
            self.rx_lock.acquire()
            for line in reversed(self.rx_data[:]):
                if line.startswith(prefix):
                    result = line.strip()
                    break
            self.rx_lock.release()
            if result:
                break
            # timeout?
            time.sleep(min(0.1, timeout))
            timeout -= 0.1
        return result

    def serial_search_regex(self, regex, timeout=0):
        """ Search for the first data matching the regular expression regex in the serial rx buffer.
        Returns match if found, None otherwise. """
        result = None
        while timeout >= 0:
            # Search for regex in rx_data
            self.rx_lock.acquire()
            # Convert rx_data list to a string to perform the search on full rx_data,
            # instead of line by line. This in case there are /r characters (EOL) in raw data.
            data = ''.join(self.rx_data)
            # Use flags=RE.DOTALL to make the '.' match any character, including '\n'.
            match = re.search(regex, data, re.DOTALL)
            if match:
                result = match.groups()
            self.rx_lock.release()
            if result is not None:
                break
            # timeout?
            time.sleep(min(0.1, timeout))
            timeout -= 0.1
        return result

    def serial_search_regex_all(self, regex, timeout=0):
        """ Search for all the lines matching the regular expression regex in the serial rx buffer.
        Returns list of line. """
        # wait for timeout if we want to get all matches
        time.sleep(timeout)
        # Search for regex in rx_data
        self.rx_lock.acquire()
        # Convert rx_data list to a string to perform the search on full rx_data,
        # instead of line by line. This in case there are /r characters (EOL) in raw data.
        data = ''.join(self.rx_data)
        # Use flags=RE.DOTALL to make the '.' match any character, including '\n'.
        result = re.findall(regex, data, re.DOTALL)
        self.rx_lock.release()
        return result

    def serial_write_data(self, data):
        """ Send data to serial port. """
        prefix = self.com_port + " > "
        if isinstance(data, bytearray):
            self.ser.write(data)
            self.ser.flushOutput()
            self.logger.debug_tx(prefix + str(binascii.hexlify(data)))
        else:
            self.sio.write(data)
            self.sio.flush()
            self.logger.debug_tx(prefix + data)
        # Wait for data to be sent
        while self.ser.out_waiting:
            pass
