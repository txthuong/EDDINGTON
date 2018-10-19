#!/usr/bin/python

"""This module contains the Logger class.
It allows logging data to a file or to the console output."""

import logging
import colorlog

class Logger:
    """Logger class."""

    DEBUG_RX_LVL = 11
    DEBUG_TX_LVL = 12

    def __init__(self, logger_name, colorise=False, level=logging.DEBUG):
        logging.addLevelName(Logger.DEBUG_RX_LVL, 'DEBUG_RX')
        logging.addLevelName(Logger.DEBUG_TX_LVL, 'DEBUG_TX')
        self.logger = colorlog.getLogger(logger_name)
        self.logger.setLevel(level)

        # log file
        formatter = logging.Formatter(
            '<%(asctime)s.%(msecs)03d {} [%(levelname)-8s]: %(message)s'.format(
                logger_name),
            datefmt='%H:%M:%S', style='%')
        file_handler = logging.FileHandler('log_{}.txt'.format(logger_name))
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # console output
        if colorise:
            formatter = colorlog.ColoredFormatter(
                '<%(asctime)s.%(msecs)03d {} [%(levelname)-8s]:'.format(logger_name) + \
                ' %(log_color)s%(message)s%(reset)s',
                datefmt='%H:%M:%S',
                reset=True,
                log_colors={
                    'DEBUG': 'green',
                    'DEBUG_RX': 'white',
                    'DEBUG_TX': 'purple',
                    'INFO': 'cyan',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                },
                secondary_log_colors={},
                style='%'
            )
        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def info(self, message):
        """Logs a message with level INFO on this logger."""
        self.logger.log(logging.INFO, message)

    def warning(self, message):
        """Logs a message with level WARNING on this logger."""
        self.logger.log(logging.WARNING, message)

    def debug_rx(self, message):
        """Logs a message with level DEBUG_RX on this logger."""
        self.logger.log(Logger.DEBUG_RX_LVL, message)

    def debug_tx(self, message):
        """Logs a message with level DEBUG_TX on this logger."""
        self.logger.log(Logger.DEBUG_TX_LVL, message)

    def error(self, message):
        """Logs a message with level ERROR on this logger."""
        self.logger.log(logging.ERROR, message)
