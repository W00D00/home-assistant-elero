"""
Support for Elero cover components.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/cover.elero/
"""
import logging
import time

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
                                 STATE_OPENING, STATE_PROBLEM, STATE_UNKNOWN)

from custom_components.elero import (COMMAND_INFO, INFO_BLOCKING,
                                     INFO_BOTTOM_POSITION_STOP,
                                     INFO_BOTTOM_POSITION_STOP_WICH_IS_INTERMEDIATE_POSITION,
                                     INFO_INTERMEDIATE_POSITION_STOP,
                                     INFO_MOVING_DOWN, INFO_MOVING_UP,
                                     INFO_NO_INFORMATION, INFO_OVERHEATED,
                                     INFO_START_TO_MOVE_DOWN,
                                     INFO_START_TO_MOVE_UP,
                                     INFO_STOPPED_IN_UNDEFINED_POSITION,
                                     INFO_TILT_VENTILATION_POSITION_STOP,
                                     INFO_TIMEOUT, INFO_TOP_POSITION_STOP,
                                     INFO_TOP_POSITION_STOP_WICH_IS_TILT_POSITION,
                                     EleroDevice)

# Python libraries/modules that you would normally install for your component.
REQUIREMENTS = []

# Other HASS components that should be setup before the platform is loaded.
DEPENDENCIES = ['elero']

_LOGGER = logging.getLogger(__name__)

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

STATES_UNDEFINED = (INFO_STOPPED_IN_UNDEFINED_POSITION,)

STATES_ERROR = (INFO_NO_INFORMATION, INFO_BLOCKING, INFO_OVERHEATED,
                INFO_TIMEOUT,
                )

POSITION_CLOSED = 0
POSITION_INTERMEDIATE = 50
POSITION_OPEN = 100

CONF_CHANNEL = 'channel'

SUPPORT_TILT = 'tilt'
CONF_TILT_MODE = 'tilt_mode'
TILT_MODE_STEPPER = 'stepper'
TILT_MODE_CONTINUOUS = 'continuous'

CONF_TILT_SLEEP = 'tilt_sleep'
DEFAULT_TILT_SLEEP = 0.1

ELERO_COVER_DEVICE_CLASSES = {
    "venetian blind": 'window',
    "roller shutter": 'window',
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
    'tilt': SUPPORT_TILT,
}

SUPPORTED_TILT_MODES = vol.All(
    vol.Lower, vol.Any(TILT_MODE_STEPPER, TILT_MODE_CONTINUOUS)
)

SUPPORTED_FEATURES_SCHEMA = vol.All(cv.ensure_list,
                                    [vol.In(SUPPORTED_FEATURES)])

# Validation of the user's configuration
COVER_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): str,
    vol.Required(CONF_CHANNEL): vol.All(
        vol.Coerce(int), vol.Range(min=1, max=15)),
    vol.Required(CONF_DEVICE_CLASS): ELERO_COVER_DEVICE_CLASSES_SCHEMA,
    vol.Required(CONF_SUPPORTED_FEATURES): SUPPORTED_FEATURES_SCHEMA,
    vol.Optional(CONF_TILT_MODE, default=TILT_MODE_STEPPER):
        vol.All(vol.Lower, vol.Any(TILT_MODE_STEPPER, TILT_MODE_CONTINUOUS)),
    vol.Optional(CONF_TILT_SLEEP, default=DEFAULT_TILT_SLEEP): float,
})

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_COVERS): vol.Schema({cv.slug: COVER_SCHEMA}),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Elero cover platform."""
    covers = []
    covers_conf = config.get(CONF_COVERS, {})
    for cover_name, cover_conf in covers_conf.items():
        covers.append(EleroCover(
            hass,
            cover_conf.get(CONF_NAME),
            cover_conf.get(CONF_CHANNEL),
            cover_conf.get(CONF_DEVICE_CLASS),
            cover_conf.get(CONF_SUPPORTED_FEATURES),
            cover_conf.get(CONF_TILT_MODE),
            cover_conf.get(CONF_TILT_SLEEP),
        ))

    add_devices(covers, True)


class EleroCover(CoverDevice, EleroDevice):
    """Representation of a Elero cover device."""

    def __init__(self, hass, name, channel, device_class, supported_features,
                 tilt_mode, tilt_sleep):
        """Init of a Elero cover."""
        EleroDevice.__init__(self, channel)
        self.hass = hass
        self._name = name
        self._channel = channel
        self._device_class = ELERO_COVER_DEVICE_CLASSES[device_class]
        # TODO: find a better method
        self._supported_features = 0
        for f in supported_features:
            if f == SUPPORT_TILT:
                if tilt_mode == TILT_MODE_STEPPER:
                    self._supported_features |= (SUPPORT_OPEN_TILT |
                                                 SUPPORT_CLOSE_TILT |
                                                 SUPPORT_SET_TILT_POSITION)
                elif tilt_mode == TILT_MODE_CONTINUOUS:
                    self._supported_features |= (SUPPORT_OPEN_TILT |
                                                 SUPPORT_CLOSE_TILT |
                                                 SUPPORT_STOP_TILT |
                                                 SUPPORT_SET_TILT_POSITION)
            else:
                self._supported_features |= SUPPORTED_FEATURES[f]

        self._tilt_mode = tilt_mode
        self._tilt_sleep = tilt_sleep

        self._available = True
        self._position = None
        self._set_position = None
        self._is_opening = None
        self._is_closing = None
        self._closed = None
        self._tilt_position = None
        self._set_tilt_position = None
        self._state = None
        self._device_response = None

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

        False if entity pushes its state to HA.
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

    def update(self):
        """Update state and attributes."""
#        self._log_device_state("1. update")
        self._device_response = self.info()
#        self._log_device_state("2. update")
        self._processing_response()

    def close_cover(self, **kwargs):
        """Close the cover."""
        self._device_response = self.down()
        self._processing_response()
        self.schedule_update_ha_state()

    def open_cover(self, **kwargs):
        """Open the cover."""
        self._device_response = self.up()
        self._processing_response()
        self.schedule_update_ha_state()

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        self._device_response = self.stop()
        self._processing_response()
        self.schedule_update_ha_state()

    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs.get(ATTR_POSITION)
        self._set_position = round(position, -1)
        _LOGGER.warning("The set cover position function is \
                        not implemented yet.")

    def close_cover_tilt(self, **kwargs):
        """Close the cover tilt."""
#        self._log_device_state("1. close_cover_tilt")
        self._device_response = self.down()
#        self._log_device_state("2. close_cover_tilt")
        self._processing_response()
        if self._tilt_mode == TILT_MODE_STEPPER:
            time.sleep(self._tilt_sleep)
            self._device_response = self.stop()
#            self._log_device_state("3. close_cover_tilt")
            self._processing_response()
        time.sleep(self._tilt_sleep)
        self.schedule_update_ha_state()

    def open_cover_tilt(self, **kwargs):
        """Open the cover tilt."""
#        self._log_device_state("1. open_cover_tilt")
        self._device_response = self.up()
#        self._log_device_state("2. open_cover_tilt")
        self._processing_response()
        if self._tilt_mode == TILT_MODE_STEPPER:
            time.sleep(self._tilt_sleep)
            self._device_response = self.stop()
#            self._log_device_state("3. open_cover_tilt")
            self._processing_response()
        time.sleep(self._tilt_sleep)
        self.schedule_update_ha_state()

    def stop_cover_tilt(self, **kwargs):
        """Stop the cover tilt."""
        self._device_response = self.stop()
        self._processing_response()
        time.sleep(self._tilt_sleep)
        self.schedule_update_ha_state()

    def set_cover_tilt_position(self, **kwargs):
        """Move the cover til to a specific position."""
        tilt_position = kwargs.get(ATTR_TILT_POSITION)
        self._set_tilt_position = round(tilt_position, -1)
        _LOGGER.warning("The set cover tilt position function is \
                        not implemented yet.")
        self.schedule_update_ha_state()

    def _log_device_state(self, command):
        _LOGGER.debug("Ch: '%s' Command: '%s' State: '%s'",
                      self._channel, command, self._device_response)

    def _processing_response(self):
        if self._device_response in STATES_CLOSED:
            self._closed = True
            self._is_closing = False
            self._is_opening = False
            self._position = POSITION_CLOSED
            self._state = STATE_CLOSED
        elif self._device_response in STATES_OPEN:
            self._closed = False
            self._is_closing = False
            self._is_opening = False
            self._position = POSITION_OPEN
            self._state = STATE_OPEN
        elif self._device_response in STATES_MOVING_DOWN:
            self._closed = False
            self._is_closing = True
            self._is_opening = False
            self._position = POSITION_INTERMEDIATE
            self._state = STATE_CLOSING
        elif self._device_response in STATES_MOVING_UP:
            self._closed = False
            self._is_closing = False
            self._is_opening = True
            self._position = POSITION_INTERMEDIATE
            self._state = STATE_OPENING
        elif self._device_response in STATES_UNDEFINED:
            self._closed = False
            self._is_closing = False
            self._is_opening = False
            self._position = POSITION_INTERMEDIATE
            self._state = STATE_UNKNOWN
        elif self._device_response in STATES_ERROR:
            self._closed = False
            self._is_closing = False
            self._is_opening = False
            self._position = None
            self._state = STATE_PROBLEM
        else:
            _LOGGER.warning("Unhandled response: '%s'", self._device_response)
            self._closed = False
            self._is_closing = False
            self._is_opening = False
            self._position = POSITION_INTERMEDIATE
            self._state = STATE_UNKNOWN
