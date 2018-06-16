"""
Support for Elero cover components.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/cover.elero/
"""

import logging

from homeassistant.const import (CONF_COVERS, CONF_NAME, CONF_DEVICE_CLASS)
from homeassistant.components.cover import CoverDevice

import custom_components.elero as elero

_LOGGER = logging.getLogger(__name__)

CONF_CHANNEL = 'channel'

HEX_FORMAT_PATTERN = '#04x'
HEX_255 = 0xFF
HEX_0 = 0x00

BIT_8 = 8

EASYCONTROL_BYTE_HEADER = 0xAA
EASYCONTROL_BYTE_LENGTH_2 = 0x02
EASYCONTROL_BYTE_LENGTH_4 = 0x04
EASYCONTROL_BYTE_LENGTH_5 = 0x05

# Wich channels are learned.
EASYCONTROL_COMMAND_CHECK = 0x4A
# The Playload will be send to all channel with bit set.
EASYCONTROL_COMMAND_SEND = 0x4C
# Get the status or position of the channel.
EASYCONTROL_COMMAND_INFO = 0x4E

EASYCONTROL_MESSAGE_CHECK = "'Easy Check' command is sent to the Stick."
EASYCONTROL_MESSAGE_SEND = "'{}' command is sent to channel {}."
EASYCONTROL_MESSAGE_INFO = "'Easy Info' command is sent to channel {}."

EASYCONTROL_RESPONSE_NO = "No response."

# The answer on Easy Check.
EASYCONTROL_ANSWER_CONFIRM = 0x4B
# The answer on Easy Send or Easy Info.
EASYCONTROL_ANSWER_ACK = 0x4D

# Playloads to send.
EASYCONTROL_PAYLOAD_UP = 0x20
EASYCONTROL_PAYLOAD_TEXT_UP = "Up"
EASYCONTROL_PAYLOAD_INTERMEDIATE = 0x44
EASYCONTROL_PAYLOAD_TEXT_INTERMEDIATE = "Intermediate"
EASYCONTROL_PAYLOAD_TILT = 0x24
EASYCONTROL_PAYLOAD_TEXT_TILT = "Tilt"
EASYCONTROL_PAYLOAD_VENTILATION = 0x24
EASYCONTROL_PAYLOAD_TEXT_VENTILATION = "Ventilation"
EASYCONTROL_PAYLOAD_DOWN = 0x40
EASYCONTROL_PAYLOAD_TEXT_DOWN = "Down"
EASYCONTROL_PAYLOAD_STOP = 0x10
EASYCONTROL_PAYLOAD_TEXT_STOP = "Stop"

# Info to receive.
EASYCONTROL_INFO_NO_INFORMATION = "No information."
EASYCONTROL_INFO_TOP_POSITION_STOP = "Top position stop."
EASYCONTROL_INFO_BOTTOM_POSITION_STOP = 'Bottom position stop.'
EASYCONTROL_INFO_INTERMEDIATE_POSITION_STOP = "Intermediate position stop."
EASYCONTROL_INFO_TILT_VENTILATION_POSITION_STOP = 'Tilt ventilation position stop.'
EASYCONTROL_INFO_BLOCKING = 'Blocking.'
EASYCONTROL_INFO_OVERHEATED = 'Overheated.'
EASYCONTROL_INFO_TIMEOUT = 'Timeout.'
EASYCONTROL_INFO_START_TO_MOVE_UP = 'Start to move up.'
EASYCONTROL_INFO_START_TO_MOVE_DOWN = 'Start to move down.'
EASYCONTROL_INFO_MOVING_UP = 'Moving up.'
EASYCONTROL_INFO_MOVING_DOWN = 'Moving down.'
EASYCONTROL_INFO_STOPPED_IN_UNDEFINED_POSITION = 'Stopped in undefined position.'
EASYCONTROL_INFO_TOP_POSITION_STOP_WICH_IS_TILT_POSITION = 'Top position stop wich is tilt position'
EASYCONTROL_INFO_BOTTOM_POSITION_STOP_WICH_IS_INTERMEDIATE_POSITION = 'Bottom position stop wich is intermediate position.'
EASYCONTROL_INFO_SWITCHING_DEVICE_SWITCHED_OFF = 'Switching device switched off.'
EASYCONTROL_INFO_SWITCHING_DEVICE_SWITCHED_ON = 'Switching device switched on.'

INFO = {0x00: EASYCONTROL_INFO_NO_INFORMATION,
        0x01: EASYCONTROL_INFO_TOP_POSITION_STOP,
        0x02: EASYCONTROL_INFO_BOTTOM_POSITION_STOP, 
        0x03: EASYCONTROL_INFO_INTERMEDIATE_POSITION_STOP,
        0x04: EASYCONTROL_INFO_TILT_VENTILATION_POSITION_STOP,
        0x05: EASYCONTROL_INFO_BLOCKING,
        0x06: EASYCONTROL_INFO_OVERHEATED,
        0x07: EASYCONTROL_INFO_TIMEOUT,
        0x08: EASYCONTROL_INFO_START_TO_MOVE_UP,
        0x09: EASYCONTROL_INFO_START_TO_MOVE_DOWN,
        0x0A: EASYCONTROL_INFO_MOVING_UP,
        0x0B: EASYCONTROL_INFO_MOVING_DOWN,
        0x0D: EASYCONTROL_INFO_STOPPED_IN_UNDEFINED_POSITION,
        0x0E: EASYCONTROL_INFO_TOP_POSITION_STOP_WICH_IS_TILT_POSITION,
        0x0F: EASYCONTROL_INFO_BOTTOM_POSITION_STOP_WICH_IS_INTERMEDIATE_POSITION,
        0x10: EASYCONTROL_INFO_SWITCHING_DEVICE_SWITCHED_OFF,
        0x11: EASYCONTROL_INFO_SWITCHING_DEVICE_SWITCHED_ON,
        }


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Elero cover platform."""
    covers_conf = config.get(CONF_COVERS, {})
    covers = []
    for cover_name, cover_conf in covers_conf.items():
        covers.append(EleroCover(
            hass, 
            cover_conf.get(CONF_NAME), 
            cover_conf.get(CONF_CHANNEL), 
            cover_conf.get(CONF_DEVICE_CLASS),
            )
        )
    
    add_devices(covers)



class EleroCover(CoverDevice):
    """Representation of a Elero cover device."""
    def __init__(self, hass, name, channel, 
                 device_class=None, supported_features=None):
        self.hass = hass
        self._name = name
        self._channel = channel
        self._device_class = device_class
        self._supported_features = None
        
        self._ser = elero.DEVICE

        self._is_opening = None
        self._is_closing = None
        self._closed = None

    @property
    def name(self):
        """Return the name of the cover."""
        return self._name

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return self._closed

    def close_cover(self, **kwargs):
        """Close the cover."""
        self._down()

    def open_cover(self, **kwargs):
        """Open the cover."""
        self._up()

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        self._stop()

    def _check(self):
        """Wich channels are learned."""
        int_list = [EASYCONTROL_BYTE_HEADER, EASYCONTROL_BYTE_LENGTH_2, 
                    EASYCONTROL_COMMAND_CHECK]
        self._send_command(int_list, EASYCONTROL_MESSAGE_CHECK)
        
        # TODO: Received an answer "Easy Confirm" with in 1 second?
    
    def _info(self):
        """ Return the current position of the cover."""
        int_list = [EASYCONTROL_BYTE_HEADER, EASYCONTROL_BYTE_LENGTH_4, 
                    EASYCONTROL_COMMAND_INFO, 
                    self._get_upper_bits(self._channel), 
                    self._get_lower_bits(self._channel)]
        self._send_command(int_list, EASYCONTROL_MESSAGE_INFO, self._channel)
        
        # TODO: Received an answer "Easy Act" with in 4 seconds?
    
    def _up(self):
        """Open the cover."""
        int_list = [EASYCONTROL_BYTE_HEADER, EASYCONTROL_BYTE_LENGTH_5, 
                    EASYCONTROL_COMMAND_SEND, 
                    self._get_upper_bits(self._channel), 
                    self._get_lower_bits(self._channel), 
                    EASYCONTROL_PAYLOAD_UP]
        self._send_command(int_list, EASYCONTROL_MESSAGE_SEND, 
                           EASYCONTROL_PAYLOAD_TEXT_UP, self._channel)
        
        # TODO: Received an answer "Easy Act" with in 4 seconds?
    
    def _intermediate(self):
        """Set the cover in intermediate position."""
        int_list = [EASYCONTROL_BYTE_HEADER, EASYCONTROL_BYTE_LENGTH_5, 
                    EASYCONTROL_COMMAND_SEND, 
                    self._get_upper_bits(self._channel), 
                    self._get_lower_bits(self._channel), 
                    EASYCONTROL_PAYLOAD_INTERMEDIATE]
        self._send_command(int_list, EASYCONTROL_MESSAGE_SEND, 
                           EASYCONTROL_PAYLOAD_TEXT_INTERMEDIATE, 
                           self._channel)
        
        # TODO: Received an answer "Easy Act" with in 4 seconds?
    
    def _tilt(self):
        """Set the cover in tilt position."""
        int_list = [EASYCONTROL_BYTE_HEADER, EASYCONTROL_BYTE_LENGTH_5, 
                    EASYCONTROL_COMMAND_SEND, 
                    self._get_upper_bits(self._channel), 
                    self._get_lower_bits(self._channel), 
                    EASYCONTROL_PAYLOAD_TILT]
        self._send_command(int_list, EASYCONTROL_MESSAGE_SEND, 
                           EASYCONTROL_PAYLOAD_TEXT_TILT, self._channel)
        
        # TODO: Received an answer "Easy Act" with in 4 seconds?
    
    def _ventilation(self):
        """Set the cover in ventilation position."""
        int_list = [EASYCONTROL_BYTE_HEADER, EASYCONTROL_BYTE_LENGTH_5, 
                    EASYCONTROL_COMMAND_SEND, 
                    self._get_upper_bits(self._channel), 
                    self._get_lower_bits(self._channel), 
                    EASYCONTROL_PAYLOAD_VENTILATION]
        self._send_command(int_list, EASYCONTROL_MESSAGE_SEND, 
                           EASYCONTROL_PAYLOAD_TEXT_VENTILATION, 
                           self._channel)
        
        # TODO: Received an answer "Easy Act" with in 4 seconds?

    def _down(self):
        """Close the cover."""
        int_list = [EASYCONTROL_BYTE_HEADER, EASYCONTROL_BYTE_LENGTH_5, 
                    EASYCONTROL_COMMAND_SEND, 
                    self._get_upper_bits(self._channel), 
                    self._get_lower_bits(self._channel), 
                    EASYCONTROL_PAYLOAD_DOWN]
        self._send_command(int_list, EASYCONTROL_MESSAGE_SEND, 
                           EASYCONTROL_PAYLOAD_TEXT_DOWN, self._channel)
        
        # TODO: Received an answer "Easy Act" with in 4 seconds?
    
    def _stop(self):
        """Stop the cover."""
        int_list = [EASYCONTROL_BYTE_HEADER, EASYCONTROL_BYTE_LENGTH_5, 
                    EASYCONTROL_COMMAND_SEND, 
                    self._get_upper_bits(self._channel), 
                    self._get_lower_bits(self._channel), 
                    EASYCONTROL_PAYLOAD_STOP]
        self._send_command(int_list, EASYCONTROL_MESSAGE_SEND, 
                           EASYCONTROL_PAYLOAD_TEXT_STOP, self._channel)
        
        # TODO: Received an answer "Easy Act" with in 4 seconds?
        
    def _send_command(self, int_list, messages, *args):
        """Write a command to the serial port. """
        int_list.append(self._calculate_checksum(*int_list))
        self._ser.serial_write(bytes(int_list))
        _LOGGER.debug(messages.format(*args))

    def _calculate_checksum(self, *args):
        """Checksum, all the sum of all bytes (Header to CS) must be 0x00."""
        return 256 - sum(args) % 256
    
    def _get_upper_bits(self, num):
        """Set upper channel bits, from 9 to 15."""
        return (1 << (num-1)) >> BIT_8
        
    def _get_lower_bits(self, num):
        """Set lower channel bits, for channel 1 to 8."""
        return (1 << (num-1)) & HEX_255
