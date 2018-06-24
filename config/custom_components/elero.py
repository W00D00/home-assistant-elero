# -*- coding: utf-8 -*-
"""
Support for Elero.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/elero/
"""
import logging
import serial

import voluptuous as vol

from homeassistant.const import (
    EVENT_HOMEASSISTANT_START, EVENT_HOMEASSISTANT_STOP, CONF_PORT)
from homeassistant.components.cover import (CoverDevice)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEVICE = None

DOMAIN = "elero"

CONF_BAUDRATE = "baudrate"
CONF_BYTESIZE = "bytesize"
CONF_PARITY = "parity"
CONF_STOPBITS = "stopbits"

DEFAULT_PORT = "/dev/ttyUSB0"
DEFAULT_BAUDRATE = 38400
DEFAULT_BYTESIZE = serial.EIGHTBITS
DEFAULT_PARITY = serial.PARITY_NONE
DEFAULT_STOPBITS = serial.STOPBITS_ONE


def setup(hass, config):
    """Set up the connection to the elero usb transmitter stick."""
    port = config[DOMAIN].get(CONF_PORT, DEFAULT_PORT)
    baudrate = int(config[DOMAIN].get(CONF_BAUDRATE, DEFAULT_BAUDRATE))
    bytesize = config[DOMAIN].get(CONF_BYTESIZE, DEFAULT_BYTESIZE)
    parity = config[DOMAIN].get(CONF_PARITY, DEFAULT_PARITY)
    stopbits = config[DOMAIN].get(CONF_STOPBITS, DEFAULT_STOPBITS)
    
    try:
        ser = serial.Serial(port, baudrate, bytesize, parity, stopbits)
    except serial.serialutil.SerialException as exc:
        _LOGGER.exception(
            "Unable to open serial port for Elero USB Stick: %s", exc)
        return False

    global DEVICE
    DEVICE = EleroTransmitter(ser)

    def close_serial_port():
        """Close the serial port."""
        ser.close()

    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, close_serial_port)

    return True


class EleroTransmitter(object):
    """Representation of an Elero Centero USB Transmitter Stick."""
    
    def __init__(self, transmitter):
        """Initialize the usb stick."""
        self._transmitter = transmitter
    
    def serial_open(self):
        """Open the serial port. """
        self._transmitter.open()
    
    def serial_close(self):
        """ Close the serial port."""
        self._transmitter.close()
    
    def serial_read(self):
        """Read the serial port."""
        return self._transmitter.read(self._transmitter.in_waiting)
    
    def serial_write(self, data):
        """Write the serial port."""
        if not self._transmitter.isOpen():
            self.serial_open()
        return self._transmitter.write(data)
