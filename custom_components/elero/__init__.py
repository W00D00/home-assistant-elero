"""Support for Elero electrical drives."""

__version__ = "3.3.1"

import logging

import homeassistant.helpers.config_validation as cv
import serial
import voluptuous as vol
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from serial.tools import list_ports

import os
import threading

# Python libraries/modules that you would normally install for your component.
REQUIREMENTS = ["pyserial>=3.4"]

# Other HASS components that should be setup before the platform is loaded.
DEPENDENCIES = []

_LOGGER = logging.getLogger(__name__)

# values to bit shift.
BIT_8 = 8

# Header for all command.
BYTE_HEADER = 0xAA

# Command lengths.
BYTE_LENGTH_2 = 0x02
BYTE_LENGTH_4 = 0x04
BYTE_LENGTH_5 = 0x05

# Configs to the serial connection.
CONF_BAUDRATE = "baudrate"
CONF_BYTESIZE = "bytesize"
CONF_PARITY = "parity"
CONF_STOPBITS = "stopbits"
CONF_TRANSMITTER_SERIAL_NUMBER = "serial_number"
CONF_TRANSMITTERS = "transmitters"
CONF_REMOTE_TRANSMITTERS = "remote_transmitters"
CONF_REMOTE_TRANSMITTERS_ADDRESS = "address"

# Easy commands.
COMMAND_CHECK = 0x4A
COMMAND_CHECH_TEXT = "Easy Check"
COMMAND_INFO = 0x4E
COMMAND_INFO_TEXT = "Info"
COMMAND_SEND = 0x4C

# Default serial info.
DEFAULT_BRAND = "elero"
DEFAULT_PRODUCT = "Transmitter Stick"

# Default serial connection details.
DEFAULT_BAUDRATE = 38400
DEFAULT_BYTESIZE = serial.EIGHTBITS
DEFAULT_PARITY = serial.PARITY_NONE
DEFAULT_STOPBITS = serial.STOPBITS_ONE

# The domain of your component. Equal to the filename of your component.
DOMAIN = "elero"

# The connected Transmitter devices.
ELERO_TRANSMITTERS = None

# values to bit shift.
HEX_255 = 0xFF

# Info to receive response.
INFO_BLOCKING = "blocking"
INFO_BOTTOM_POSITION_STOP = "bottom position stop"
INFO_BOTTOM_POS_STOP_WICH_INT_POS = "bottom position stop wich is intermediate position"
INFO_INTERMEDIATE_POSITION_STOP = "intermediate position stop"
INFO_MOVING_DOWN = "moving down"
INFO_MOVING_UP = "moving up"
INFO_NO_INFORMATION = "no information"
INFO_OVERHEATED = "overheated"
INFO_START_TO_MOVE_DOWN = "start to move down"
INFO_START_TO_MOVE_UP = "start to move up"
INFO_STOPPED_IN_UNDEFINED_POSITION = "stopped in undefined position"
INFO_SWITCHING_DEVICE_SWITCHED_OFF = "switching device switched off"
INFO_SWITCHING_DEVICE_SWITCHED_ON = "switching device switched on"
INFO_TILT_VENTILATION_POS_STOP = "tilt ventilation position stop"
INFO_TIMEOUT = "timeout"
INFO_TOP_POSITION_STOP = "top position stop"
INFO_TOP_POS_STOP_WICH_TILT_POS = "top position stop wich is tilt position"
INFO_UNKNOWN = "unknown response"

INFO = {
    0x00: INFO_NO_INFORMATION,
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

# Playloads to send.
PAYLOAD_DOWN = 0x40
PAYLOAD_DOWN_TEXT = "Down"
PAYLOAD_INTERMEDIATE_POS = 0x44
PAYLOAD_INTERMEDIATE_POS_TEXT = "Intermediate position"
PAYLOAD_STOP = 0x10
PAYLOAD_STOP_TEXT = "Stop"
PAYLOAD_UP = 0x20
PAYLOAD_UP_TEXT = "Up"
PAYLOAD_VENTILATION_POS_TILTING = 0x24
PAYLOAD_VENTILATION_POS_TILTING_TEXT = "Tilt/ventilation"

# Easy response lengths.
RESPONSE_LENGTH_CHECK = 6
RESPONSE_LENGTH_INFO = 7
RESPONSE_LENGTH_SEND = 7

ELERO_TRANSMITTER_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_TRANSMITTER_SERIAL_NUMBER): str,
        vol.Optional(CONF_BAUDRATE, default=DEFAULT_BAUDRATE): cv.positive_int,
        vol.Optional(CONF_BYTESIZE, default=DEFAULT_BYTESIZE): cv.positive_int,
        vol.Optional(CONF_PARITY, default=DEFAULT_PARITY): str,
        vol.Optional(CONF_STOPBITS, default=DEFAULT_STOPBITS): cv.positive_int,
    }
)

ELERO_REMOTE_TRANSMITTER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TRANSMITTER_SERIAL_NUMBER): str,
        vol.Required(CONF_REMOTE_TRANSMITTERS_ADDRESS): str
    }
)

# Validation of the user's configuration.
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_TRANSMITTERS): [ELERO_TRANSMITTER_SCHEMA],
                vol.Optional(CONF_REMOTE_TRANSMITTERS): [ELERO_REMOTE_TRANSMITTER_SCHEMA] 
            }
        ),
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    global ELERO_TRANSMITTERS
    elero_config = config.get(DOMAIN)
    transmitters_config = elero_config.get(CONF_TRANSMITTERS)
    remote_transmitters_config = elero_config.get(CONF_REMOTE_TRANSMITTERS)

    ELERO_TRANSMITTERS = EleroTransmitters(transmitters_config)
    ELERO_TRANSMITTERS.discover()
    ELERO_TRANSMITTERS.connect_remote_transmitters(remote_transmitters_config)

    def close_serial_ports(event):
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
        _LOGGER.info(f"Elero lib version: {__version__}")

    def discover(self):
        """Discover the local connected Elero Transmitter Sticks."""

        for cp in list_ports.comports():
            found_elero_stick = True if (
                cp and cp.manufacturer
                and DEFAULT_BRAND in cp.manufacturer
                and cp.product
                and DEFAULT_PRODUCT in cp.product
                and cp.serial_number
            ) else False
            preset_elero_stick = False
            try:
                #check if device matches and if serial number was set
                if cp.device == os.environ["ELERO_DEVICE"] and os.environ["ELERO_SERIAL_NUMBER"]:
                    preset_elero_stick = True
                    elero_serial_number = os.environ["ELERO_SERIAL_NUMBER"]
                    _LOGGER.info(
                        f"Elero Transmitter Stick was configured manually: {os.environ['ELERO_DEVICE']}"
                        f"with serial number {os.environ['ELERO_SERIAL_NUMBER']}"
                    )
            except KeyError:
                # env variables not set, moving on
                pass

            if found_elero_stick or preset_elero_stick:
                # use discovered serial number
                if found_elero_stick:
                    elero_serial_number = cp.serial_number
                _LOGGER.info(
                    f"Elero Transmitter Stick is found on port: "
                    f"'{cp.device}' with serial number: '{elero_serial_number}'."
                )

                if self.config and elero_serial_number in self.config:
                    baudrate = self.config[elero_serial_number].get(CONF_BAUDRATE)
                    bytesize = self.config[elero_serial_number].get(CONF_BYTESIZE)
                    parity = self.config[elero_serial_number].get(CONF_PARITY)
                    stopbits = self.config[elero_serial_number].get(CONF_STOPBITS)
                else:
                    baudrate = DEFAULT_BAUDRATE
                    bytesize = DEFAULT_BYTESIZE
                    parity = DEFAULT_PARITY
                    stopbits = DEFAULT_STOPBITS

                elero_transmitter = EleroTransmitter(
                    cp.device, elero_serial_number, baudrate, bytesize, parity, stopbits
                )
                elero_transmitter.init_serial()

                if elero_transmitter.get_transmitter_state():
                    if elero_serial_number not in self.transmitters:
                        self.transmitters[elero_serial_number] = elero_transmitter
                    else:
                        _LOGGER.error(
                            f"'{elero_serial_number}' transmitter is already added!"
                        )
    def connect_remote_transmitters(self, config):
        """Find remote transmitters."""

        _LOGGER.debug("Connect Elero remote transmitters")
        
        if not config:  # No remote transmitters configured
            return
        
        for remote_config in config:
            _LOGGER.debug(f"Try to connect to remote transmitter "
                          f"'{remote_config[CONF_TRANSMITTER_SERIAL_NUMBER]} with " 
                          f"address '{remote_config[CONF_REMOTE_TRANSMITTERS_ADDRESS]}'")
            
            serial_number = remote_config[CONF_TRANSMITTER_SERIAL_NUMBER]
            address = remote_config[CONF_REMOTE_TRANSMITTERS_ADDRESS]

            elero_transmitter = EleroRemoteTransmitter(serial_number, address)
            elero_transmitter.init_serial()

            if elero_transmitter.get_transmitter_state():
                    if serial_number not in self.transmitters:
                        self.transmitters[serial_number] = elero_transmitter
                    else:
                        _LOGGER.error(
                            f"'{serial_number}' transmitter has already been added!"
                        )

    def get_transmitter(self, serial_number):
        """Return the given transmitter."""
        if serial_number in self.transmitters:
            return self.transmitters[serial_number]
        else:
            _LOGGER.error(f"The transmitter '{serial_number}' doesn't exist!")
            return None

    def close_transmitters(self):
        """Close the serial connection of the transmitters."""
        for _, t in self.transmitters.items():
            t.close_serial()


class EleroTransmitter(object):
    """Representation of an Elero Centero USB Transmitter Stick."""

    def __init__(self, serial_device, serial_number, baudrate, bytesize, parity, stopbits):
        """Initialize a elero transmitter."""
        self._port = serial_device
        self._serial_number = serial_number
        self._baudrate = baudrate
        self._bytesize = bytesize
        self._parity = parity
        self._stopbits = stopbits
        self._threading_lock = threading.Lock()
        # Setup the serial connection to the transmitter.
        self._serial = None
        self._learned_channels = {}

        self._threading_lock = threading.Lock()
        
    def init_serial(self):
        """Setup serial connection and get learned channels from the transmitter."""

        # Setup the serial connection to the transmitter.
        self.init_serial_port()
        # Get the learned channels from the transmitter.
        if self._serial:
            self.check()

    def init_serial_port(self):
        """Init the serial port to the transmitter."""
        try:
            self._serial = serial.Serial(
                self._port,
                self._baudrate,
                self._bytesize,
                self._parity,
                self._stopbits,
                timeout=2,
                write_timeout=2,
            )
        except serial.serialutil.SerialException as exc:
            _LOGGER.exception(
                f"Unable to open serial port for '{self._serial_number}' to"
                f"the Transmitter Stick: '{exc}'."
            )

    def log_out_serial_port_details(self):
        """Log out the details of the serial connection."""
        _LOGGER.debug(f"Transmitter stick on port '{self._port}' serial: '{self._serial_number}'.")

    def close_serial(self):
        """Close the serial connection of the transmitter."""
        self._serial.close()

    def get_transmitter_state(self):
        """Return with transmitter is usable or not."""
        return True if self._serial else False

    def get_serial_number(self):
        """Return the ID of the transmitter."""
        return self._serial_number

    def __get_check_command(self):
        """Create a hex list to Check command."""
        int_list = [BYTE_HEADER, BYTE_LENGTH_2, COMMAND_CHECK]
        return int_list

    def check(self):
        """Wich channels are learned.

        Should be received an answer "Easy Confirm" with in 1 second.
        """
        int_list = self.__get_check_command()
        self.__process_command(COMMAND_CHECH_TEXT, int_list, 0, RESPONSE_LENGTH_CHECK)

    def __set_learned_channels(self, resp):
        """Store learned channels."""
        self._learned_channels = dict.fromkeys(resp["chs"])
        chs = " ".join(map(str, list(self._learned_channels.keys())))
        _LOGGER.debug(
            f"The taught channels on the '{self._serial_number}' "
            f"transmitter are '{chs}'."
        )

    def set_channel(self, channel, obj):
        """Set the channel if it is learned."""
        if channel in self._learned_channels:
            self._learned_channels[channel] = obj
            return True
        else:
            _LOGGER.error(
                f"The '{channel}' channel is not taught to the "
                f"'{self._serial_number}' transmitter."
            )
            return False

    def __get_info_command(self, channel):
        """Create a hex list to the Info command."""
        int_list = [
            BYTE_HEADER,
            BYTE_LENGTH_4,
            COMMAND_INFO,
            self.__set_upper_channel_bits(channel),
            self.__set_lower_channel_bits(channel),
        ]
        return int_list

    def info(self, channel):
        """Return the current state of the cover.

        Should be received an answer "Easy Act" with in 4 seconds.
        """
        int_list = self.__get_info_command(channel)
        self.__process_command(
            COMMAND_INFO_TEXT, int_list, channel, RESPONSE_LENGTH_INFO
        )

    def __get_up_command(self, channel):
        """Create a hex list to Open command."""
        int_list = [
            BYTE_HEADER,
            BYTE_LENGTH_5,
            COMMAND_SEND,
            self.__set_upper_channel_bits(channel),
            self.__set_lower_channel_bits(channel),
            PAYLOAD_UP,
        ]
        return int_list

    def up(self, channel):
        """Open the cover.

        Should be received an answer "Easy Act" with in 4 seconds.
        """
        self.__process_command(
            PAYLOAD_UP_TEXT,
            self.__get_up_command(channel),
            channel,
            RESPONSE_LENGTH_SEND,
        )

    def __get_down_command(self, channel):
        """Create a hex list to Close command."""
        int_list = [
            BYTE_HEADER,
            BYTE_LENGTH_5,
            COMMAND_SEND,
            self.__set_upper_channel_bits(channel),
            self.__set_lower_channel_bits(channel),
            PAYLOAD_DOWN,
        ]
        return int_list

    def down(self, channel):
        """Close the cover.

        Should be received an answer "Easy Act" with in 4 seconds.
        """
        self.__process_command(
            PAYLOAD_DOWN_TEXT,
            self.__get_down_command(channel),
            channel,
            RESPONSE_LENGTH_SEND,
        )

    def __get_stop_command(self, channel):
        """Create a hex list to the Stop command."""
        int_list = [
            BYTE_HEADER,
            BYTE_LENGTH_5,
            COMMAND_SEND,
            self.__set_upper_channel_bits(channel),
            self.__set_lower_channel_bits(channel),
            PAYLOAD_STOP,
        ]
        return int_list

    def stop(self, channel):
        """Stop the cover.

        Should be received an answer "Easy Act" with in 4 seconds.
        """
        self.__process_command(
            PAYLOAD_STOP_TEXT,
            self.__get_stop_command(channel),
            channel,
            RESPONSE_LENGTH_SEND,
        )

    def __get_intermediate_command(self, channel):
        """Create a hex list to the intermediate command."""
        int_list = [
            BYTE_HEADER,
            BYTE_LENGTH_5,
            COMMAND_SEND,
            self.__set_upper_channel_bits(channel),
            self.__set_lower_channel_bits(channel),
            PAYLOAD_INTERMEDIATE_POS,
        ]
        return int_list

    def intermediate(self, channel):
        """Set the cover in intermediate position.

        Should be received an answer "Easy Act" with in 4 seconds.
        """
        self.__process_command(
            PAYLOAD_INTERMEDIATE_POS_TEXT,
            self.__get_intermediate_command(channel),
            channel,
            RESPONSE_LENGTH_SEND,
        )

    def __get_ventilation_tilting_command(self, channel):
        """Create a hex list to the ventilation command."""
        int_list = [
            BYTE_HEADER,
            BYTE_LENGTH_5,
            COMMAND_SEND,
            self.__set_upper_channel_bits(channel),
            self.__set_lower_channel_bits(channel),
            PAYLOAD_VENTILATION_POS_TILTING,
        ]
        return int_list

    def ventilation_tilting(self, channel):
        """Set the cover in ventilation/tilting position.

        Should be received an answer "Easy Act" with in 4 seconds.
        """
        self.__process_command(
            PAYLOAD_VENTILATION_POS_TILTING_TEXT,
            self.__get_ventilation_tilting_command(channel),
            channel,
            RESPONSE_LENGTH_SEND,
        )

    def __process_command(self, command_text, int_list, channel, resp_length):
        """Ensure the recursive func handling."""
        int_list.append(self.__calculate_checksum(*int_list))
        bytes_data = self.__create_serial_data(int_list)

        attempt = 0
        while attempt < 4:
            attempt += 1
            try:
                with self._threading_lock:
                    if not self._serial.is_open:
                        self._serial.open()
                    self._serial.write(bytes_data)
                    ser_resp = self._serial.read(resp_length)
                if ser_resp:
                    resp = self.__parse_response(ser_resp, channel)
                    rsp = resp["status"]
                    chs = resp["chs"]
                    _LOGGER.debug(
                        f"Send '{command_text}' command to the transmitter: "
                        f"'{self._serial_number}' ch: '{channel}' serial command: "
                        f"'{bytes_data}' serial response: '{ser_resp}' "
                        f"response: '{rsp}' from ch(s): '{chs}' "
                        f"attempt: '{attempt}'."
                    )
                    # Easy Check.
                    if command_text == COMMAND_CHECH_TEXT:
                        self.__set_learned_channels(resp)
                    else:
                        self.__process_response(resp)
                    break
            except serial.serialutil.SerialException as exc:
                _LOGGER.debug(
                    f"Problem communicating with transmitter: "
                    f"'{self._serial_number}' send command: '{command_text}' "
                    f"ch: '{channel}' serial command: '{bytes_data}' "
                    f"attempt: '{attempt}' exception: '{exc}'"
                )
                self.init_serial_port()

    def __process_response(self, resp):
        """Read the response form the device."""
        # Reply to the appropriate channel.
        for ch in resp["chs"]:
            # Call back the channel with its result.
            if ch in self._learned_channels:
                self._learned_channels[ch](resp)
            else:
                _LOGGER.error(
                    f"The channel is not learned '{self._serial_number}' "
                    f"on the transmitter: '{ch}'."
                )

    def __parse_response(self, ser_resp, channel):
        """Parse the serial data as a response."""
        response = {
            "bytes": None,
            "header": None,
            "length": None,
            "command": None,
            "ch_h": None,
            "ch_l": None,
            "chs": set(),
            "status": None,
            "cs": None,
        }
        response["bytes"] = ser_resp
        resp_length = len(ser_resp)
        # Common parts.
        response["header"] = ser_resp[0]
        response["length"] = ser_resp[1]
        response["command"] = ser_resp[2]
        response["ch_h"] = self.__get_upper_channel_bits(ser_resp[3])
        response["ch_l"] = self.__get_lower_channel_bits(ser_resp[4])
        response["chs"] = set(response["ch_h"] + response["ch_l"])
        # Easy Confirmed (the answer on Easy Check).
        if resp_length == RESPONSE_LENGTH_CHECK:
            response["cs"] = ser_resp[5]
        # Easy Ack (the answer on Easy Info).
        elif resp_length == RESPONSE_LENGTH_SEND:
            if ser_resp[5] in INFO:
                response["status"] = INFO[ser_resp[5]]
            else:
                response["status"] = INFO_UNKNOWN
                _LOGGER.error(
                    f"Transmitter: '{self._serial_number}' ch: '{channel}' "
                    f"status is unknown: '{ser_resp[5]:X}'."
                )
            response["cs"] = ser_resp[6]
        else:
            _LOGGER.error(
                f"Transmitter: '{self._serial_number}' ch: '{channel}' "
                f"unknown response: '{ser_resp}'."
            )
            response["status"] = INFO_UNKNOWN

        return response

    def __calculate_checksum(self, *args):
        """Calculate checksum.

        All the sum of all bytes (Header to CS) must be 0x00.
        """
        return (256 - sum(args)) % 256

    def __create_serial_data(self, int_list):
        """Convert integers to bytes for serial communication."""
        bytes_data = bytes(int_list)
        return bytes_data

    def __set_upper_channel_bits(self, channel):
        """Set upper channel bits, for channel 9 to 15."""
        res = (1 << (channel - 1)) >> BIT_8
        return res

    def __set_lower_channel_bits(self, channel):
        """Set lower channel bits, for channel 1 to 8."""
        res = (1 << (channel - 1)) & HEX_255
        return res

    def __get_upper_channel_bits(self, byt):
        """Return the set channel numbers from 9 to 15."""
        channels = []
        for i in range(0, 8):
            if (byt >> i) & 1 == 1:
                ch = i + 9
                channels.append(ch)

        return tuple(channels)

    def __get_lower_channel_bits(self, byt):
        """Return the set channel numbers from 1 to 8."""
        channels = []
        for i in range(0, 8):
            if (byt >> i) & 1 == 1:
                ch = i + 1
                channels.append(ch)

        return tuple(channels)


class EleroRemoteTransmitter(EleroTransmitter):
    """Representation of a remotely connected Elero Centero USB Transmitter Stick.
    
       Using ser2net
    
    """
    def __init__(self, serial_number, address):
        
        self._address = address
        super().__init__(None, serial_number, None, None, None, None, )

    
    def init_serial(self):
        """Setup serial connection and get learned channels from the transmitter."""
        
        # Setup the serial connection to the transmitter.
        self.init_serial_port()
        # Get the learned channels from the transmitter.
        if self._serial:
            self.check()


    def init_serial_port(self):
        """Init the serial port to the transmitter."""

        url = f"socket://{self._address}"
        # https://pyserial.readthedocs.io/en/latest/url_handlers.html#urls
        try:
            self._serial = serial.serial_for_url(url)
            _LOGGER.info(
                    f"Elero Transmitter Stick is remotely connected to '{self._address}' "
                    f"with serial number: '{self._serial_number}'."
                )
        except serial.serialutil.SerialException as exc:
            _LOGGER.exception(
                f"Unable to connect to remote serial port '{url}' for serial "
                f"number {self._serial_number}: '{exc}'."
            )

    def log_out_serial_port_details(self):
        """Log out the details of the serial connection."""
        _LOGGER.debug(f"Remote Transmitter stick on address '{self._address}'.")
