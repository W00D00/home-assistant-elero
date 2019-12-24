"""
Support for Elero cover components.

For more details about this component, please refer to the documentation
https://home-assistant.io/components/cover.elero/
"""
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.cover import (ATTR_POSITION, ATTR_TILT_POSITION,
                                            SUPPORT_CLOSE, SUPPORT_CLOSE_TILT,
                                            SUPPORT_OPEN, SUPPORT_OPEN_TILT,
                                            SUPPORT_SET_POSITION,
                                            SUPPORT_SET_TILT_POSITION,
                                            SUPPORT_STOP, SUPPORT_STOP_TILT,
                                            CoverDevice)
from homeassistant.components.light import PLATFORM_SCHEMA
from homeassistant.const import (CONF_COVERS, CONF_DEVICE_CLASS, CONF_NAME,
                                 STATE_CLOSED, STATE_CLOSING, STATE_OPEN,
                                 STATE_OPENING, STATE_UNKNOWN)

import custom_components.elero as elero
from custom_components.elero import (CONF_TRANSMITTER_SERIAL_NUMBER,
                                     INFO_BLOCKING,
                                     INFO_BOTTOM_POS_STOP_WICH_INT_POS,
                                     INFO_BOTTOM_POSITION_STOP,
                                     INFO_INTERMEDIATE_POSITION_STOP,
                                     INFO_MOVING_DOWN, INFO_MOVING_UP,
                                     INFO_NO_INFORMATION, INFO_OVERHEATED,
                                     INFO_START_TO_MOVE_DOWN,
                                     INFO_START_TO_MOVE_UP,
                                     INFO_STOPPED_IN_UNDEFINED_POSITION,
                                     INFO_SWITCHING_DEVICE_SWITCHED_OFF,
                                     INFO_SWITCHING_DEVICE_SWITCHED_ON,
                                     INFO_TILT_VENTILATION_POS_STOP,
                                     INFO_TIMEOUT,
                                     INFO_TOP_POS_STOP_WICH_TILT_POS,
                                     INFO_TOP_POSITION_STOP,
                                     RESPONSE_LENGTH_INFO,
                                     RESPONSE_LENGTH_SEND)

# Python libraries/modules that you would normally install for your component.
REQUIREMENTS = []

# Other HASS components that should be setup before the platform is loaded.
DEPENDENCIES = ['elero']

_LOGGER = logging.getLogger(__name__)

POSITION_CLOSED = 0
POSITION_TILT_VENTILATION = 25
POSITION_UNDEFINED = 50
POSITION_INTERMEDIATE = 75
POSITION_OPEN = 100

STATE_STOPPED = 'stopped'
STATE_TILT_VENTILATION = "ventilation/tilt"
STATE_INTERMEDIATE = 'intermediate'
STATE_UNDEFINED = 'undefined'

ATTR_ELERO_STATE = 'elero_state'

# Should be if the transmitter bug is corrected.
CONF_CHANNELS = 'channels'
# It is needed because of the transmitter has a channel handling bug.
CONF_CHANNEL = 'channel'

ELERO_COVER_DEVICE_CLASSES = {
    "venetian blind": 'window',
    "roller shutter": 'window',
    "interior shading": 'window',
    'awning': 'window',
    "rolling door": 'garage',
}

ELERO_COVER_DEVICE_CLASSES_SCHEMA = vol.All(vol.Lower,
                                            vol.In(ELERO_COVER_DEVICE_CLASSES))

CONF_SUPPORTED_FEATURES = 'supported_features'

SUPPORTED_FEATURES = {
    'up': SUPPORT_OPEN,
    'down': SUPPORT_CLOSE,
    'stop': SUPPORT_STOP,
    'set_position': SUPPORT_SET_POSITION,
    'open_tilt': SUPPORT_OPEN_TILT,
    'close_tilt': SUPPORT_CLOSE_TILT,
    'stop_tilt': SUPPORT_STOP_TILT,
    'set_tilt_position': SUPPORT_SET_TILT_POSITION,
}

SUPPORTED_FEATURES_SCHEMA = vol.All(cv.ensure_list,
                                    [vol.In(SUPPORTED_FEATURES)])

# Should be if the transmitter bug is corrected.
CHANNEL_NUMBERS_SCHEMA = vol.All(cv.ensure_list,
                                 [vol.Range(min=1, max=15)])

# It is needed because of the transmitter has a channel handling bug.
CHANNEL_NUMBERS_SCHEMA = vol.All(vol.Coerce(int), vol.Range(min=1, max=15))

# Validation of the user's configuration
COVER_SCHEMA = vol.Schema({
    vol.Required(CONF_TRANSMITTER_SERIAL_NUMBER): str,
    vol.Required(CONF_NAME): str,
    vol.Required(CONF_CHANNEL): CHANNEL_NUMBERS_SCHEMA,
    vol.Required(CONF_DEVICE_CLASS): ELERO_COVER_DEVICE_CLASSES_SCHEMA,
    vol.Required(CONF_SUPPORTED_FEATURES): SUPPORTED_FEATURES_SCHEMA,
})

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_COVERS): vol.Schema({cv.slug: COVER_SCHEMA}),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Elero cover platform."""
    covers = []
    covers_conf = config.get(CONF_COVERS, {})
    for _, cover_conf in covers_conf.items():
        transmitter = elero.ELERO_TRANSMITTERS.get_transmitter(
            cover_conf.get(CONF_TRANSMITTER_SERIAL_NUMBER))
        if not transmitter:
            _LOGGER.error("Elero - the transmitter '{}' "
                          "of the '{}' - '{}' channel is "
                          "non-existent transmitter!"
                          .format(
                            cover_conf.get(CONF_TRANSMITTER_SERIAL_NUMBER),
                            cover_conf.get(CONF_CHANNEL),
                            cover_conf.get(CONF_NAME)))
            continue

        covers.append(EleroCover(
            hass,
            transmitter,
            cover_conf.get(CONF_NAME),
            cover_conf.get(CONF_CHANNEL),
            cover_conf.get(CONF_DEVICE_CLASS),
            cover_conf.get(CONF_SUPPORTED_FEATURES),
        ))

    add_devices(covers, True)


class EleroCover(CoverDevice):
    """Representation of a Elero cover device."""

    def __init__(self, hass, transmitter, name, channel, device_class,
                 supported_features):
        """Init of a Elero cover."""
        self.hass = hass
        self._transmitter = transmitter
        self._name = name
        self._channel = channel
        self._device_class = ELERO_COVER_DEVICE_CLASSES[device_class]

        self._supported_features = 0
        for f in supported_features:
            self._supported_features |= SUPPORTED_FEATURES[f]

        self._available = self._transmitter.set_channel(self._channel,
                                                        self.response_handler)
        self._position = None
        self._is_opening = None
        self._is_closing = None
        self._closed = None
        self._tilt_position = None
        self._state = None
        self._elero_state = None
        self._response = dict()

    @property
    def name(self):
        """Return the name of the cover."""
        return self._name

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return self._device_class

    @property
    def supported_features(self):
        """Flag supported features."""
        return self._supported_features

    @property
    def should_poll(self):
        """Return True if entity has to be polled for state.

        Because of you can use other remote control (like MultiTel2)
        next to the HA in your system and the status of the Elero devices
        may change therefore it is necessary to monitor their statuses.
        """
        return True

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    @property
    def current_cover_position(self):
        """Return the current position of the cover.

        None is unknown, 0 is closed, 100 is fully open.
        """
        return self._position

    @property
    def current_cover_tilt_position(self):
        """Return the current tilt position of the cover."""
        return self._tilt_position

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

    @property
    def state(self):
        """Return the state of the cover."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        data = {}

        elero_state = self._elero_state
        if elero_state is not None:
            data[ATTR_ELERO_STATE] = self._elero_state

        return data

    def update(self):
        """Get the device sate and update its attributes and state."""
        self._transmitter.info(self._channel)
        self._transmitter.get_response(RESPONSE_LENGTH_INFO, self._channel)

    def close_cover(self, **kwargs):
        """Close the cover."""
        self._transmitter.down(self._channel)
        self._closed = False
        self._is_closing = True
        self._is_opening = False
        self._state = STATE_CLOSING
        self._position = POSITION_CLOSED
        self._tilt_position = POSITION_UNDEFINED
        self.schedule_update_ha_state()

    def open_cover(self, **kwargs):
        """Open the cover."""
        self._transmitter.up(self._channel)
        self._closed = False
        self._is_closing = False
        self._is_opening = True
        self._state = STATE_OPENING
        self._position = POSITION_OPEN
        self._tilt_position = POSITION_UNDEFINED
        self.schedule_update_ha_state()

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        self._transmitter.stop(self._channel)
        self._closed = False
        self._is_closing = False
        self._is_opening = False
        self._state = STATE_STOPPED
        self._position = POSITION_UNDEFINED
        self._tilt_position = POSITION_UNDEFINED
        self.schedule_update_ha_state()

    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs.get(ATTR_POSITION)
        if position < 13:
            self.close_cover()
        elif position > 13 and position < 50:
            self.cover_ventilation_tilting_position()
        elif position > 50 and position < 88:
            self.cover_intermediate_position()
        elif position > 88:
            self.open_cover()
        else:
            _LOGGER.error("Elero - Wrong Position slider data: {}"
                          .format(position))

    def cover_ventilation_tilting_position(self, **kwargs):
        """Move into the ventilation/tilting position."""
        self._transmitter.ventilation_tilting(self._channel)
        self._closed = False
        self._is_closing = False
        self._is_opening = False
        self._state = STATE_TILT_VENTILATION
        self._position = POSITION_TILT_VENTILATION
        self._tilt_position = POSITION_TILT_VENTILATION
        self.schedule_update_ha_state()

    def cover_intermediate_position(self, **kwargs):
        """Move into the intermediate position."""
        self._transmitter.intermediate(self._channel)
        self._closed = False
        self._is_closing = False
        self._is_opening = False
        self._state = STATE_INTERMEDIATE
        self._position = POSITION_INTERMEDIATE
        self._tilt_position = POSITION_INTERMEDIATE
        self.schedule_update_ha_state()

    def close_cover_tilt(self, **kwargs):
        """Close the cover tilt."""
        self.cover_ventilation_tilting_position()

    def open_cover_tilt(self, **kwargs):
        """Open the cover tilt."""
        self.cover_intermediate_position()

    def stop_cover_tilt(self, **kwargs):
        """Stop the cover tilt."""
        self.stop_cover()

    def set_cover_tilt_position(self, **kwargs):
        """Move the cover tilt to a specific position."""
        tilt_position = kwargs.get(ATTR_TILT_POSITION)
        if tilt_position < 50:
            self.cover_ventilation_tilting_position()
        elif tilt_position > 50:
            self.cover_intermediate_position()
        else:
            _LOGGER.error("Elero - Wrong Tilt Position slider data: {}"
                          .format(tilt_position))

    def request_response(self, resp_length):
        """Set state variables based on device response."""
        self._transmitter.get_response(resp_length, self._channel)

    def response_handler(self, response):
        """Callback function to the response from the Transmitter."""
        self._response = response
        self.set_states()

    def set_states(self):
        """Set the state of the cover."""
        self._elero_state = self._response['status']
        if self._response['status'] == INFO_NO_INFORMATION:
            self._closed = None
            self._is_closing = None
            self._is_opening = None
            self._state = STATE_UNKNOWN
            self._position = None
            self._tilt_position = None
        elif self._response['status'] == INFO_TOP_POSITION_STOP:
            self._closed = False
            self._is_closing = False
            self._is_opening = False
            self._state = STATE_OPEN
            self._position = POSITION_OPEN
            self._tilt_position = POSITION_UNDEFINED
        elif self._response['status'] == INFO_BOTTOM_POSITION_STOP:
            self._closed = True
            self._is_closing = False
            self._is_opening = False
            self._state = STATE_CLOSED
            self._position = POSITION_CLOSED
            self._tilt_position = POSITION_UNDEFINED
        elif self._response['status'] == INFO_INTERMEDIATE_POSITION_STOP:
            self._closed = False
            self._is_closing = False
            self._is_opening = False
            self._state = STATE_INTERMEDIATE
            self._position = POSITION_INTERMEDIATE
            self._tilt_position = POSITION_INTERMEDIATE
        elif self._response['status'] == INFO_TILT_VENTILATION_POS_STOP:
            self._closed = False
            self._is_closing = False
            self._is_opening = False
            self._state = STATE_TILT_VENTILATION
            self._position = POSITION_TILT_VENTILATION
            self._tilt_position = POSITION_TILT_VENTILATION
        elif self._response['status'] == INFO_START_TO_MOVE_UP:
            self._closed = False
            self._is_closing = False
            self._is_opening = True
            self._state = STATE_OPENING
            self._position = POSITION_UNDEFINED
            self._tilt_position = POSITION_UNDEFINED
        elif self._response['status'] == INFO_START_TO_MOVE_DOWN:
            self._closed = False
            self._is_closing = True
            self._is_opening = False
            self._state = STATE_CLOSING
            self._position = POSITION_UNDEFINED
            self._tilt_position = POSITION_UNDEFINED
        elif self._response['status'] == INFO_MOVING_UP:
            self._closed = False
            self._is_closing = False
            self._is_opening = True
            self._state = STATE_OPENING
            self._position = POSITION_UNDEFINED
            self._tilt_position = POSITION_UNDEFINED
        elif self._response['status'] == INFO_MOVING_DOWN:
            self._closed = False
            self._is_closing = True
            self._is_opening = False
            self._state = STATE_CLOSING
            self._position = POSITION_UNDEFINED
            self._tilt_position = POSITION_UNDEFINED
        elif self._response['status'] == INFO_STOPPED_IN_UNDEFINED_POSITION:
            self._closed = False
            self._is_closing = False
            self._is_opening = False
            self._state = STATE_UNDEFINED
            self._position = POSITION_UNDEFINED
            self._tilt_position = POSITION_UNDEFINED
        elif self._response['status'] == INFO_TOP_POS_STOP_WICH_TILT_POS:
            self._closed = False
            self._is_closing = False
            self._is_opening = False
            self._state = STATE_TILT_VENTILATION
            self._position = POSITION_TILT_VENTILATION
            self._tilt_position = POSITION_TILT_VENTILATION
        elif self._response['status'] == INFO_BOTTOM_POS_STOP_WICH_INT_POS:
            self._closed = True
            self._is_closing = False
            self._is_opening = False
            self._state = STATE_INTERMEDIATE
            self._position = POSITION_INTERMEDIATE
            self._tilt_position = POSITION_INTERMEDIATE
        elif self._response['status'] in (INFO_BLOCKING, INFO_OVERHEATED,
                                          INFO_TIMEOUT):
            self._closed = None
            self._is_closing = None
            self._is_opening = None
            self._state = STATE_UNKNOWN
            self._position = None
            self._tilt_position = None
            _LOGGER.error("Elero - transmitter: '{}' ch: '{}' "
                          "Error response: '{}'."
                          .format(self._transmitter.get_serial_number(),
                                  self._channel, self._response['status']))

        elif self._response['status'] in (
                INFO_SWITCHING_DEVICE_SWITCHED_ON,
                INFO_SWITCHING_DEVICE_SWITCHED_OFF):
            self._closed = None
            self._is_closing = None
            self._is_opening = None
            self._state = STATE_UNKNOWN
            self._position = None
            self._tilt_position = None
        else:
            self._closed = None
            self._is_closing = None
            self._is_opening = None
            self._state = STATE_UNKNOWN
            self._position = None
            self._tilt_position = None
            _LOGGER.error("Elero - transmitter: '{}' ch: '{}' "
                          "Unhandled response: '{}'."
                          .format(self._transmitter.get_serial_number(),
                                  self._channel, self._response['status']))
