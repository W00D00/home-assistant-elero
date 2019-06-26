"""
Support for Elero electrical drives.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/elero/
"""
import logging

import homeassistant.helpers.config_validation as cv
import serial
import voluptuous as vol
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from serial.tools import list_ports

# Python libraries/modules that you would normally install for your component.
REQUIREMENTS = ['pyserial==3.4']

# Other HASS components that should be setup before the platform is loaded.
DEPENDENCIES = []

_LOGGER = logging.getLogger(__name__)

# The domain of your component. Equal to the filename of your component.
DOMAIN = 'elero'

# The connected Transmitter devices.
ELERO_TRANSMITTERS = None

# Configs to the serial connection.
CONF_TRANSMITTERS = 'transmitters'
CONF_TRANSMITTER_SERIAL_NUMBER = 'serial_number'
CONF_BAUDRATE = 'baudrate'
CONF_BYTESIZE = 'bytesize'
CONF_PARITY = 'parity'
CONF_STOPBITS = 'stopbits'

# Default serial info
DEFAULT_BRAND = 'elero'
DEFAULT_PRODUCT = 'Transmitter Stick'

# Default serial connection details.
DEFAULT_BAUDRATE = 38400
DEFAULT_BYTESIZE = serial.EIGHTBITS
DEFAULT_PARITY = serial.PARITY_NONE
DEFAULT_STOPBITS = serial.STOPBITS_ONE

# values to bit shift.
HEX_255 = 0xFF
BIT_8 = 8

# Header for all command.
BYTE_HEADER = 0xAA
# command lengths
BYTE_LENGTH_2 = 0x02
BYTE_LENGTH_4 = 0x04
BYTE_LENGTH_5 = 0x05

# Wich channels are learned.
COMMAND_CHECK = 0x4A
# required response lenth.
RESPONSE_LENGTH_CHECK = 6
# The Playload will be send to all channel with bit set.
COMMAND_SEND = 0x4C
# required response lenth.
RESPONSE_LENGTH_SEND = 7
# Get the status or position of the channel.
COMMAND_INFO = 0x4E
# Required response lenth.
RESPONSE_LENGTH_INFO = 7
# for Serial error handling
NO_SERIAL_RESPONSE = b''

# Playloads to send.
PAYLOAD_STOP = 0x10
PAYLOAD_STOP_TEXT = "stop"
PAYLOAD_UP = 0x20
PAYLOAD_UP_TEXT = "up"
PAYLOAD_VENTILATION_POS_TILTING = 0x24
PAYLOAD_VENTILATION_POS_TILTING_TEXT = "ventilation position/tilting"
PAYLOAD_DOWN = 0x40
PAYLOAD_DOWN_TEXT = "down"
PAYLOAD_INTERMEDIATE_POS = 0x44
PAYLOAD_INTERMEDIATE_POS_TEXT = "intermediate position/tilting"

# Info to receive response.
INFO_UNKNOWN = "unknown response"
INFO_NO_INFORMATION = "no information"
INFO_TOP_POSITION_STOP = "top position stop"
INFO_BOTTOM_POSITION_STOP = "bottom position stop"
INFO_INTERMEDIATE_POSITION_STOP = "intermediate position stop"
INFO_TILT_VENTILATION_POS_STOP = "tilt ventilation position stop"
INFO_BLOCKING = "blocking"
INFO_OVERHEATED = "overheated"
INFO_TIMEOUT = "timeout"
INFO_START_TO_MOVE_UP = "start to move up"
INFO_START_TO_MOVE_DOWN = "start to move down"
INFO_MOVING_UP = "moving up"
INFO_MOVING_DOWN = "moving down"
INFO_STOPPED_IN_UNDEFINED_POSITION = "stopped in undefined position"
INFO_TOP_POS_STOP_WICH_TILT_POS = "top position stop wich is tilt position"
INFO_BOTTOM_POS_STOP_WICH_INT_POS = \
    "bottom position stop wich is intermediate position"
INFO_SWITCHING_DEVICE_SWITCHED_OFF = "switching device switched off"
INFO_SWITCHING_DEVICE_SWITCHED_ON = "switching device switched on"

INFO = {0x00: INFO_NO_INFORMATION,
        0x01: INFO_TOP_POSITION_STOP,
        0x02: INFO_BOTTOM_POSITION_STOP,
        0x03: INFO_INTERMEDIATE_POSITION_STOP,
        0x04: INFO_TILT_VENTILATION_POS_STOP,
        0x05: INFO_BLOCKING,
        0x06: INFO_OVERHEATED,
        0x07: INFO_TIMEOUT,
        0x08: INFO_START_TO_MOVE_UP,
        0x09: INFO_START_TO_MOVE_DOWN,
        0x0A: INFO_MOVING_UP,
        0x0B: INFO_MOVING_DOWN,
        0x0D: INFO_STOPPED_IN_UNDEFINED_POSITION,
        0x0E: INFO_TOP_POS_STOP_WICH_TILT_POS,
        0x0F: INFO_BOTTOM_POS_STOP_WICH_INT_POS,
        0x10: INFO_SWITCHING_DEVICE_SWITCHED_OFF,
        0x11: INFO_SWITCHING_DEVICE_SWITCHED_ON,
        }

ELERO_TRANSMITTER_SCHEMA = vol.Schema({
    vol.Optional(CONF_TRANSMITTER_SERIAL_NUMBER): str,
    vol.Optional(CONF_BAUDRATE, default=DEFAULT_BAUDRATE): cv.positive_int,
    vol.Optional(CONF_BYTESIZE, default=DEFAULT_BYTESIZE): cv.positive_int,
    vol.Optional(CONF_PARITY, default=DEFAULT_PARITY): str,
    vol.Optional(CONF_STOPBITS, default=DEFAULT_STOPBITS): cv.positive_int,
})

# Validation of the user's configuration.
CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_TRANSMITTERS): [ELERO_TRANSMITTER_SCHEMA],
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    global ELERO_TRANSMITTERS
    elero_config = config.get(DOMAIN)
    transmitters_config = elero_config.get(CONF_TRANSMITTERS)
    ELERO_TRANSMITTERS = EleroTransmitters(transmitters_config)
    ELERO_TRANSMITTERS.discover()

    def close_serial_ports():
        """Close the serial port."""
        ELERO_TRANSMITTERS.close_transmitters()

    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, close_serial_ports)

    # Return boolean to indicate that initialization was successfully.
    return True


class EleroTransmitters(object):
    """Container for the Elero Centero USB Transmitter Sticks."""

    def __init__(self, config):
        """Initialize the usb sticks."""
        self.config = config
        self.transmitters = {}

    def discover(self):
        """Discover the connected Elero Transmitter Sticks."""
        for cp in list_ports.comports():
            if (cp and cp.manufacturer and DEFAULT_BRAND in cp.manufacturer and
                    cp.product and DEFAULT_PRODUCT in cp.product):
                _LOGGER.info(
                    "Elero - an Elero Transmitter Stick is found on port: '{}'"
                    " with serial number: '{}'"
                    .format(cp.device, cp.serial_number))

                if (self.config and cp.serial_number and
                        cp.serial_number in self.config):
                    baudrate = self.config[cp.serial_number].get(CONF_BAUDRATE)
                    bytesize = self.config[cp.serial_number].get(CONF_BYTESIZE)
                    parity = self.config[cp.serial_number].get(CONF_PARITY)
                    stopbits = self.config[cp.serial_number].get(CONF_STOPBITS)
                else:
                    baudrate = DEFAULT_BAUDRATE
                    bytesize = DEFAULT_BYTESIZE
                    parity = DEFAULT_PARITY
                    stopbits = DEFAULT_STOPBITS

                elero_transmitter = EleroTransmitter(
                    cp, baudrate, bytesize, parity, stopbits)

                if elero_transmitter.get_transmitter_state():
                    if cp.serial_number not in self.transmitters:
                        self.transmitters[cp.serial_number] = elero_transmitter
                    else:
                        _LOGGER.error(
                            "Elero - '{}' transmitter is already added!"
                            .format(cp.serial_number))

    def get_transmitter(self, serial_number):
        """Return the given transmitter."""
        if serial_number in self.transmitters:
            return self.transmitters[serial_number]
        else:
            _LOGGER.error("Elero - the transmitter '{}' is not exist!"
                          .format(serial_number))
            return None

    def close_transmitters(self):
        """Close the serial connection of the transmitters."""
        for sn, t in self.transmitters.items():
            t.close_serial()


class EleroTransmitter(object):
    """Representation of an Elero Centero USB Transmitter Stick."""

    def __init__(self, serial_port, baudrate, bytesize, parity, stopbits):
        """Initialization of a elero transmitter."""
        self.serial_port = serial_port
        self._serial_number = self.serial_port.serial_number
        self._port = self.serial_port.device
        self._baudrate = baudrate
        self._bytesize = bytesize
        self._parity = parity
        self._stopbits = stopbits
        # setup the serial connection to the transmitter
        self._serial = None
        self._init_serial()
        # get the learned channels from the transmitter
        self._learned_channels = {}
        if self._serial:
            self.check()

    def _init_serial(self):
        """Init the serial port to the transmitter."""
        try:
            self._serial = serial.Serial(self._port, self._baudrate,
                                         self._bytesize, self._parity,
                                         self._stopbits)
        except serial.serialutil.SerialException as exc:
            _LOGGER.exception("Elero - unable to open serial port for '{}' to"
                              "the Transmitter Stick: '{}'"
                              .format(self._serial_number, exc))

    def log_out_serial_port_details(self):
        """Log out the details of the serial connection."""
        details = self.serial_port.__dict__
        _LOGGER.debug("Elero - transmitter stick on port '{}' details: {}"
                      .format(self._port, details))

    def close_serial(self):
        """Close the serial connection of the transmitter."""
        self._serial.close()

    def get_transmitter_state(self):
        """The transmitter is usable or not."""
        return True if self._serial else False

    def get_serial_number(self):
        """Return the ID of the transmitter."""
        return self._serial_number

    def _get_check_command(self):
        """Create a hex list to Check command."""
        int_list = [BYTE_HEADER, BYTE_LENGTH_2,
                    COMMAND_CHECK]
        return int_list

    def check(self):
        """Wich channels are learned.

        Should be received an answer "Easy Confirm" with in 1 second.
        """
        self._send_command(self._get_check_command(), 0)
        ser_resp = self._read_response(RESPONSE_LENGTH_CHECK, 0)
        resp = self._parse_response(ser_resp, 0)
        self._learned_channels = dict.fromkeys(resp['chs'])
        _LOGGER.debug("The taught channels on the '{}' transmitter are '{}'."
                      .format(self._serial_number, ' '.join(
                        map(str, list(self._learned_channels.keys())))))

    def set_channel(self, channel, obj):
        """Set the channel if it is learned."""
        if channel in self._learned_channels:
            self._learned_channels[channel] = obj
            return True
        else:
            _LOGGER.error("The '{}' channel is not taught to the "
                          "'{}' transmitter.".format(channel,
                                                     self._serial_number))
            return False

    def _get_info_command(self, channel):
        """Create a hex list to the Info command."""
        int_list = [BYTE_HEADER, BYTE_LENGTH_4,
                    COMMAND_INFO,
                    self._set_upper_channel_bits(channel),
                    self._set_lower_channel_bits(channel)]
        return int_list

    def info(self, channel):
        """Return the current state of the cover.

        Should be received an answer "Easy Act" with in 4 seconds.
        """
        self._send_command(self._get_info_command(channel), channel)

    def _get_up_command(self, channel):
        """Create a hex list to Open command."""
        int_list = [BYTE_HEADER, BYTE_LENGTH_5,
                    COMMAND_SEND,
                    self._set_upper_channel_bits(channel),
                    self._set_lower_channel_bits(channel),
                    PAYLOAD_UP]
        return int_list

    def up(self, channel):
        """Open the cover.

        Should be received an answer "Easy Act" with in 4 seconds.
        """
        self._send_command(self._get_up_command(channel), channel)

    def _get_down_command(self, channel):
        """Create a hex list to Close command."""
        int_list = [BYTE_HEADER, BYTE_LENGTH_5,
                    COMMAND_SEND,
                    self._set_upper_channel_bits(channel),
                    self._set_lower_channel_bits(channel),
                    PAYLOAD_DOWN]
        return int_list

    def down(self, channel):
        """Close the cover.

        Should be received an answer "Easy Act" with in 4 seconds.
        """
        self._send_command(self._get_down_command(channel), channel)

    def _get_stop_command(self, channel):
        """Create a hex list to the Stop command."""
        int_list = [BYTE_HEADER, BYTE_LENGTH_5,
                    COMMAND_SEND,
                    self._set_upper_channel_bits(channel),
                    self._set_lower_channel_bits(channel),
                    PAYLOAD_STOP]
        return int_list

    def stop(self, channel):
        """Stop the cover.

        Should be received an answer "Easy Act" with in 4 seconds.
        """
        self._send_command(self._get_stop_command(channel), channel)

    def _get_intermediate_command(self, channel):
        """Create a hex list to the intermediate command."""
        int_list = [BYTE_HEADER, BYTE_LENGTH_5,
                    COMMAND_SEND,
                    self._set_upper_channel_bits(channel),
                    self._set_lower_channel_bits(channel),
                    PAYLOAD_INTERMEDIATE_POS]
        return int_list

    def intermediate(self, channel):
        """Set the cover in intermediate position.

        Should be received an answer "Easy Act" with in 4 seconds.
        """
        self._send_command(self._get_intermediate_command(channel), channel)

    def _get_ventilation_tilting_command(self, channel):
        """Create a hex list to the ventilation command."""
        int_list = [BYTE_HEADER, BYTE_LENGTH_5,
                    COMMAND_SEND,
                    self._set_upper_channel_bits(channel),
                    self._set_lower_channel_bits(channel),
                    PAYLOAD_VENTILATION_POS_TILTING]
        return int_list

    def ventilation_tilting(self, channel):
        """Set the cover in ventilation position.

        Should be received an answer "Easy Act" with in 4 seconds.
        """
        self._send_command(self._get_ventilation_tilting_command(channel),
                           channel)

    def _read_response(self, resp_length, channel):
        """Get the serial data from the serial port."""
        if not self._serial.isOpen():
            self._serial.open()
        ser_resp = self._serial.read(resp_length)
        _LOGGER.debug("Elero - transmitter: '{}' ch: '{}' "
                      "serial response: '{}'"
                      .format(self._serial_number, channel, ser_resp))
        return ser_resp

    def _parse_response(self, ser_resp, channel):
        """Parse the serial data as a response."""
        response = {'bytes': None,
                    'header': None,
                    'length': None,
                    'command': None,
                    'ch_h': None,
                    'ch_l': None,
                    'chs': set(),
                    'status': None,
                    'cs': None,
                    }

        response['bytes'] = ser_resp
        # No response or serial data
        if not ser_resp:
            response['status'] = INFO_NO_INFORMATION
            return
        resp_length = len(ser_resp)
        # Common parts
        response['header'] = ser_resp[0]
        response['length'] = ser_resp[1]
        response['command'] = ser_resp[2]
        response['ch_h'] = self._get_upper_channel_bits(ser_resp[3])
        response['ch_l'] = self._get_lower_channel_bits(ser_resp[4])
        response['chs'] = set(
            response['ch_h'] + response['ch_l'])
        # Easy Confirmed (the answer on Easy Check)
        if resp_length == RESPONSE_LENGTH_CHECK:
            response['cs'] = ser_resp[5]
        # Easy Ack (the answer on Easy Info)
        elif resp_length == RESPONSE_LENGTH_SEND:
            if ser_resp[5] in INFO:
                response['status'] = INFO[ser_resp[5]]
            else:
                response['status'] = INFO_UNKNOWN
                _LOGGER.warning("Elero - transmitter: '{}' ch: '{}' "
                                "status is unknown: '{}'"
                                .format(self._serial_number, channel,
                                        ser_resp[5]))
            response['cs'] = ser_resp[6]
        else:
            _LOGGER.warning("Elero - transmitter: '{}' ch: '{}' "
                            "unknown response: '{}'"
                            .format(self._serial_number, channel, ser_resp))
            response['status'] = INFO_UNKNOWN

        return response

    def get_response(self, resp_length, channel):
        """Read the response form the device."""
        ser_resp = self._read_response(resp_length, channel)
        resp = self._parse_response(ser_resp, channel)
        # reply to the appropriate channel TODO
        if len(resp['chs']) == 1:
            ch = resp['chs'].pop()
            # call back the channel with its result
            self._learned_channels[ch](resp)
        else:
            _LOGGER.error(
                "Elero - The response contains more than one channel."
                .format(resp['chs']))

    def _send_command(self, int_list, channel):
        """Write out a command to the serial port."""
        int_list.append(self._calculate_checksum(*int_list))
        bytes_data = self._create_serial_data(int_list)
        _LOGGER.debug("Elero - transmitter: '{}' ch: '{}' "
                      "serial command: '{}'"
                      .format(self._serial_number, channel, bytes_data))
        if not self._serial.isOpen():
            self._serial.open()
        self._serial.write(bytes_data)

    def _calculate_checksum(self, *args):
        """Calculate checksum.

        All the sum of all bytes (Header to CS) must be 0x00.
        """
        return (256 - sum(args)) % 256

    def _create_serial_data(self, int_list):
        """Convert integers to bytes for serial communication."""
        bytes_data = bytes(int_list)
        return bytes_data

    def _set_upper_channel_bits(self, channel):
        """Set upper channel bits, for channel 9 to 15."""
        res = (1 << (channel-1)) >> BIT_8
        return res

    def _set_lower_channel_bits(self, channel):
        """Set lower channel bits, for channel 1 to 8."""
        res = (1 << (channel-1)) & HEX_255
        return res

    def _get_upper_channel_bits(self, byt):
        """The set channel numbers from 9 to 15."""
        channels = []
        for i in range(0, 8):
            if (byt >> i) & 1 == 1:
                ch = i + 9
                channels.append(ch)

        return tuple(channels)

    def _get_lower_channel_bits(self, byt):
        """The set channel numbers from 1 to 8."""
        channels = []
        for i in range(0, 8):
            if (byt >> i) & 1 == 1:
                ch = i + 1
                channels.append(ch)

        return tuple(channels)
