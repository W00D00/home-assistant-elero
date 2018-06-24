# -*- coding: utf-8 -*-
"""
Support for Elero cover components.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/cover.elero/
"""
import time
import logging

from homeassistant.const import (CONF_COVERS, CONF_NAME, CONF_DEVICE_CLASS, 
                                 STATE_OPEN, STATE_OPENING, 
                                 STATE_CLOSED, STATE_CLOSING, 
                                 STATE_UNKNOWN, STATE_PROBLEM
                                 )
from homeassistant.components.cover import (
    CoverDevice, SUPPORT_OPEN, SUPPORT_CLOSE, SUPPORT_STOP)
from homeassistant.components.cover import CoverDevice
from homeassistant.helpers.event import track_utc_time_change

import custom_components.elero as elero


_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['elero']

CONF_CHANNEL = "channel"
CHANNEL_NUMBERS = range(1, 16)

HEX_FORMAT_PATTERN = "#04x"
HEX_255 = 0xFF
HEX_0 = 0x00

BIT_8 = 8

BYTE_HEADER = 0xAA
BYTE_LENGTH_2 = 0x02
BYTE_LENGTH_4 = 0x04
BYTE_LENGTH_5 = 0x05

# Wich channels are learned.
COMMAND_CHECK = 0x4A
# The Playload will be send to all channel with bit set.
COMMAND_SEND = 0x4C
# Get the status or position of the channel.
COMMAND_INFO = 0x4E

MESSAGE_CHECK = "'Easy Check' command is sent to the Stick."
MESSAGE_SEND = "'{}' command is sent to channel {}."
MESSAGE_INFO = "'Easy Info' command is sent to channel {}."

RESPONSE_UNKNOW = "unknown response"
RESPONSE_NO = "no response"

# Playloads to send.
PAYLOAD_UP = 0x20
PAYLOAD_TEXT_UP = "Up"
PAYLOAD_INTERMEDIATE = 0x44
PAYLOAD_TEXT_INTERMEDIATE = "Intermediate"
PAYLOAD_TILT = 0x24
PAYLOAD_TEXT_TILT = "Tilt"
PAYLOAD_VENTILATION = 0x24
PAYLOAD_TEXT_VENTILATION = "Ventilation"
PAYLOAD_DOWN = 0x40
PAYLOAD_TEXT_DOWN = "Down"
PAYLOAD_STOP = 0x10
PAYLOAD_TEXT_STOP = "Stop"

# Info to receive.
INFO_UNKNOWN = "Unknown info respons"
INFO_NO_INFORMATION = "no information"
INFO_TOP_POSITION_STOP = "top position stop"
INFO_BOTTOM_POSITION_STOP = "bottom position stop"
INFO_INTERMEDIATE_POSITION_STOP = "intermediate position stop"
INFO_TILT_VENTILATION_POSITION_STOP = "tilt ventilation position stop"
INFO_BLOCKING = "blocking"
INFO_OVERHEATED = "overheated"
INFO_TIMEOUT = "timeout"
INFO_START_TO_MOVE_UP = "start to move up"
INFO_START_TO_MOVE_DOWN = "start to move down"
INFO_MOVING_UP = "moving up"
INFO_MOVING_DOWN = "moving down"
INFO_STOPPED_IN_UNDEFINED_POSITION = "stopped in undefined position"
INFO_TOP_POSITION_STOP_WICH_IS_TILT_POSITION = \
    "top position stop wich is tilt position"
INFO_BOTTOM_POSITION_STOP_WICH_IS_INTERMEDIATE_POSITION = \
    "bottom position stop wich is intermediate position"
INFO_SWITCHING_DEVICE_SWITCHED_OFF = "switching device switched off"
INFO_SWITCHING_DEVICE_SWITCHED_ON = "switching device switched on"

INFO = {0x00: INFO_NO_INFORMATION,
        0x01: INFO_TOP_POSITION_STOP,
        0x02: INFO_BOTTOM_POSITION_STOP, 
        0x03: INFO_INTERMEDIATE_POSITION_STOP,
        0x04: INFO_TILT_VENTILATION_POSITION_STOP,
        0x05: INFO_BLOCKING,
        0x06: INFO_OVERHEATED,
        0x07: INFO_TIMEOUT,
        0x08: INFO_START_TO_MOVE_UP,
        0x09: INFO_START_TO_MOVE_DOWN,
        0x0A: INFO_MOVING_UP,
        0x0B: INFO_MOVING_DOWN,
        0x0D: INFO_STOPPED_IN_UNDEFINED_POSITION,
        0x0E: INFO_TOP_POSITION_STOP_WICH_IS_TILT_POSITION,
        0x0F: INFO_BOTTOM_POSITION_STOP_WICH_IS_INTERMEDIATE_POSITION,
        0x10: INFO_SWITCHING_DEVICE_SWITCHED_OFF,
        0x11: INFO_SWITCHING_DEVICE_SWITCHED_ON,
        }

STATES_OPEN = (INFO_TOP_POSITION_STOP, 
               INFO_TOP_POSITION_STOP_WICH_IS_TILT_POSITION, 
               INFO_INTERMEDIATE_POSITION_STOP, 
               INFO_TILT_VENTILATION_POSITION_STOP, 
               )

STATES_CLOSED = (INFO_BOTTOM_POSITION_STOP, 
                 INFO_BOTTOM_POSITION_STOP_WICH_IS_INTERMEDIATE_POSITION, 
                 )

STATES_MOVING_UP = (INFO_START_TO_MOVE_UP, INFO_MOVING_UP)

STATES_MOVING_DOWN = (INFO_START_TO_MOVE_DOWN, INFO_MOVING_DOWN)

STATES_UNDEFINED = (INFO_STOPPED_IN_UNDEFINED_POSITION)

STATES_ERROR = (INFO_NO_INFORMATION, INFO_BLOCKING, INFO_OVERHEATED, 
                INFO_TIMEOUT, 
                )

POSITION_CLOSED = 0
POSITION_INTERMEDIATE = 50
POSITION_OPEN = 100


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
            (SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_STOP)
            )
        )
    
    add_devices(covers)


class EleroCover(CoverDevice):
    """Representation of a Elero cover device."""
    def __init__(self, hass, name, channel, device_class, supported_features):
        self.hass = hass
        self._name = name
        self._channel = channel
        self._device_class = device_class
        self._supported_features = supported_features
        
        self._position = None
        self._is_opening = None
        self._is_closing = None
        self._closed = None
        self._state = None
        self._available = True
        self._unsub_listener_cover = None
        
        self._transmitter = elero.DEVICE
        
        self.update()

    @property
    def name(self):
        """Return the name of the cover."""
        return self._name

    @property
    def should_poll(self):
        """Return True if entity has to be polled for state.
        
        False if entity pushes its state to HA.
        """
        return True

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return self._device_class

    @property
    def supported_features(self):
        """Flag supported features."""
        return self._supported_features

    @property
    def current_cover_position(self):
        """Return the current position of the cover.
        
        None is unknown, 0 is closed, 100 is fully open.
        """
        return self._position

    @property
    def is_opening(self):
        """Return if the cover is opening or not."""
        return self._is_opening

    @property
    def is_closing(self):
        """Return if the cover is closing or not."""
        return self._is_closing

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return self._closed

    def update(self):
        """Update device state."""
        self._info()
        resp = self._get_response(COMMAND_INFO, 1)
        
        if resp in STATES_CLOSED:
            self._closed = True
            self._is_closing = False
            self._is_opening = False
            self._position = POSITION_CLOSED
            self._state = STATE_CLOSED
        elif resp in STATES_OPEN:
            self._closed = False
            self._is_closing = False
            self._is_opening = False
            self._position = POSITION_OPEN
            self._state = STATE_OPEN
        elif resp in STATES_MOVING_DOWN:
            self._closed = False
            self._is_closing = True
            self._is_opening = False
            self._position = POSITION_INTERMEDIATE
            self._state = STATE_CLOSING
        elif resp in STATES_MOVING_UP:
            self._closed = False
            self._is_closing = False
            self._is_opening = True
            self._position = POSITION_INTERMEDIATE
            self._state = STATE_OPENING
        elif resp in STATES_UNDEFINED:
            self._closed = False
            self._is_closing = False
            self._is_opening = False
            self._position = POSITION_INTERMEDIATE
            self._state = STATE_UNKNOWN
        elif resp in STATES_ERROR:
            self._closed = False
            self._is_closing = False
            self._is_opening = False
            self._position = None
            self._state = STATE_PROBLEM
        else:
            _LOGGER.warning("Unhandled response: %s", resp)
            self._closed = False
            self._is_closing = False
            self._is_opening = False
            self._position = POSITION_INTERMEDIATE
            self._state = STATE_UNKNOWN
            
        _LOGGER.info("Current status of the channel %s is %s", self._channel, 
                      self._state)

    def _start_watcher(self, command):
        """Start watcher."""
        _LOGGER.debug("Starting Watcher for command: %s ", command)
        if self._unsub_listener_cover is None:
            self._unsub_listener_cover = track_utc_time_change(
                self.hass, self._check_state)

    def _check_state(self, now):
        """Check the state of the service during an operation."""
        self.schedule_update_ha_state(True)

    """
    
    HA Cover specific commands.
    
    """
    
    def close_cover(self, **kwargs):
        """Close the cover."""
        if self._state not in [STATE_CLOSED, STATE_CLOSING]:
            self._down()
            self._start_watcher('close')

    def open_cover(self, **kwargs):
        """Open the cover."""
        if self._state not in [STATE_OPEN, STATE_OPENING]:
            self._up()
            self._start_watcher('open')

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        self._stop()
        self._start_watcher('stop')

    """
    
    Elero specific commands.
    
    """

    def _check(self):
        """Wich channels are learned.
        Should be received an answer "Easy Confirm" with in 1 second.
        """
        int_list = [BYTE_HEADER, BYTE_LENGTH_2, 
                    COMMAND_CHECK]
        self._send_command(int_list, MESSAGE_CHECK)
    
    def _info(self):
        """ Return the current state of the cover.
        Should be received an answer "Easy Act" with in 4 seconds.
        """
        int_list = [BYTE_HEADER, BYTE_LENGTH_4, 
                    COMMAND_INFO, 
                    self._get_upper_channel_bits(self._channel), 
                    self._get_lower_channel_bits(self._channel)]
        self._send_command(int_list, MESSAGE_INFO, self._channel)
    
    def _up(self):
        """Open the cover.
        Should be received an answer "Easy Act" with in 4 seconds.
        """
        int_list = [BYTE_HEADER, BYTE_LENGTH_5, 
                    COMMAND_SEND, 
                    self._get_upper_channel_bits(self._channel), 
                    self._get_lower_channel_bits(self._channel), 
                    PAYLOAD_UP]
        self._send_command(int_list, MESSAGE_SEND, 
                           PAYLOAD_TEXT_UP, self._channel)
    
    def _down(self):
        """Close the cover.
        Should be received an answer "Easy Act" with in 4 seconds.
        """
        int_list = [BYTE_HEADER, BYTE_LENGTH_5, 
                    COMMAND_SEND, 
                    self._get_upper_channel_bits(self._channel), 
                    self._get_lower_channel_bits(self._channel), 
                    PAYLOAD_DOWN]
        self._send_command(int_list, MESSAGE_SEND, 
                           PAYLOAD_TEXT_DOWN, self._channel)
    
    def _stop(self):
        """Stop the cover.
        Should be received an answer "Easy Act" with in 4 seconds.
        """
        int_list = [BYTE_HEADER, BYTE_LENGTH_5, 
                    COMMAND_SEND, 
                    self._get_upper_channel_bits(self._channel), 
                    self._get_lower_channel_bits(self._channel), 
                    PAYLOAD_STOP]
        self._send_command(int_list, MESSAGE_SEND, 
                           PAYLOAD_TEXT_STOP, self._channel)

    def _intermediate(self):
        """Set the cover in intermediate position.
        Should be received an answer "Easy Act" with in 4 seconds.
        """
        int_list = [BYTE_HEADER, BYTE_LENGTH_5, 
                    COMMAND_SEND, 
                    self._get_upper_channel_bits(self._channel), 
                    self._get_lower_channel_bits(self._channel), 
                    PAYLOAD_INTERMEDIATE]
        self._send_command(int_list, MESSAGE_SEND, 
                           PAYLOAD_TEXT_INTERMEDIATE, 
                           self._channel)
    
    def _tilt(self):
        """Set the cover in tilt position.
        Should be received an answer "Easy Act" with in 4 seconds.
        """
        int_list = [BYTE_HEADER, BYTE_LENGTH_5, 
                    COMMAND_SEND, 
                    self._get_upper_channel_bits(self._channel), 
                    self._get_lower_channel_bits(self._channel), 
                    PAYLOAD_TILT]
        self._send_command(int_list, MESSAGE_SEND, 
                           PAYLOAD_TEXT_TILT, self._channel)
    
    def _ventilation(self):
        """Set the cover in ventilation position.
        Should be received an answer "Easy Act" with in 4 seconds.
        """
        int_list = [BYTE_HEADER, BYTE_LENGTH_5, 
                    COMMAND_SEND, 
                    self._get_upper_channel_bits(self._channel), 
                    self._get_lower_channel_bits(self._channel), 
                    PAYLOAD_VENTILATION]
        self._send_command(int_list, MESSAGE_SEND, 
                           PAYLOAD_TEXT_VENTILATION, 
                           self._channel)
    
    """
    
    Functions to the processing of the Elero commands.
    
    """
    
    def _send_command(self, int_list, messages, *args):
        """Write a command to the serial port. """
        int_list.append(self._calculate_checksum(*int_list))
        written_bytes = self._transmitter.serial_write(bytes(int_list))
        _LOGGER.info(messages.format(*args))
        _LOGGER.debug("%s bytes written.", written_bytes)
        
        return written_bytes
    
    def _calculate_checksum(self, *args):
        """Checksum, all the sum of all bytes (Header to CS) must be 0x00."""
        return (256 - sum(args)) % 256
    
    def _get_upper_channel_bits(self, num):
        """Set upper channel bits, from 9 to 15."""
        return (1 << (num-1)) >> BIT_8
        
    def _get_lower_channel_bits(self, num):
        """Set lower channel bits, for channel 1 to 8."""
        return (1 << (num-1)) & HEX_255
    
    def _get_channels_from_response(self, byt):
        """ """
        channels = []
        for i in range(0, 16):
            if (byt >> i) & 1 == 1:
                ch = i + 1
                channels.append(ch)
        
        return tuple(channels)
    
    def _get_response(self, command, sleep=0):
        """Get the response from the serial port."""
        time.sleep(sleep)
        resp = self._transmitter.serial_read()
        resp_len = len(resp)
        if command == COMMAND_CHECK and resp_len == 6:
            return self._answer_on_check(resp)
        elif command == COMMAND_SEND and resp_len == 7:
            return self._answer_on_send(resp)
        elif command == COMMAND_INFO and resp_len == 7:
            return self._answer_on_info(resp)
        elif resp_len > 7:
            _LOGGER.error("Response to the %s command is too long: %s", 
                          command, resp)
        else:
            _LOGGER.warning("{}: {}".format(RESPONSE_UNKNOW, resp))
            return RESPONSE_UNKNOW
    
    def _answer_on_check(self, resp):
        """Which channels are leared on the transmitter."""
        channels = ()
        # Upper channels
        channels = channels + self._get_channels_from_response(resp[3])
        # Lower channels
        channels = channels + self._get_channels_from_response(resp[4])
        
        return channels
    
    def _answer_on_send(self, resp):
        """ """
        if resp[5] in INFO:
            return INFO[resp[5]]
        else:
            _LOGGER.warning("{}: {}".format(INFO_UNKNOWN, resp))
            return INFO_UNKNOWN
    
    def _answer_on_info(self, resp):
        """ """
        return self._answer_on_send(resp)
