# -*- coding: utf-8 -*-
"""
Elero Unittest.

Unittesting the Elero lib.
"""
import unittest
from unittest.mock import Mock

from custom_components import elero as elero_platform
from custom_components.cover import elero as elero_component


class EleroUnittest(unittest.TestCase):
    """Unittest to Elero."""

    def setUp(self):
        """Seting up the unittest."""
        self._serial = Mock()
        self.elero_transmitter = elero_platform.EleroTransmitter(
            1, self._serial)
        self.elero_device = elero_platform.EleroDevice(
            self.elero_transmitter, 1)

        self.elero_cover = elero_component.EleroCover(None,
                                                      self.elero_transmitter,
                                                      'Étkező', 7,
                                                      'venetian blind',
                                                      ('up', 'down',
                                                       'stop'))

    def test_name(self):
        """Testing the name method."""
        self.assertEqual(self.elero_cover.name, 'Étkező')

    def test_device_class(self):
        """Testing the device_class method."""
        self.assertEqual(self.elero_cover.device_class, 'window')

    def test_supported_features(self):
        """Testing the supported_features method."""
        self.assertEqual(self.elero_cover.supported_features, 11)

    def test_should_poll(self):
        """Testing the should_poll method."""
        self.assertEqual(self.elero_cover.should_poll, True)

    def test_available(self):
        """Testing the available method."""
        self.assertEqual(self.elero_cover.available, True)

    def test_current_cover_position(self):
        """Testing the current_cover_position method."""
        self.assertEqual(self.elero_cover.current_cover_position, None)

    def test_current_cover_tilt_position(self):
        """Testing the current_cover_tilt_position method."""
        self.assertEqual(self.elero_cover.current_cover_tilt_position, None)

    def test_is_opening(self):
        """Testing the is_opening method."""
        self.assertEqual(self.elero_cover.is_opening, None)

    def test_is_closing(self):
        """Testing the is_closing method."""
        self.assertEqual(self.elero_cover.is_closing, None)

    def test_is_closed(self):
        """Testing the is_closed method."""
        self.assertEqual(self.elero_cover.is_closed, None)

    def test_state(self):
        """Testing the state method."""
        self.assertEqual(self.elero_cover.state, None)

    # EleroCover class
    def test_get_transmitter_id(self):
        """Testing the get_transmitter_id method."""
        self.assertEqual(self.elero_transmitter.get_transmitter_id(), 1)

    def test_read_response(self):
        """Testing the get_response method."""
        self._serial.read = Mock(
            return_value=b'')
        self.assertEqual(self.elero_device._read_response(0), b'')

    def test_reset_response(self):
        """Testing the _reset_response method."""
        self.assertEqual(self.elero_device._reset_response(), None)
        self.assertEqual(self.elero_device._response['bytes'], None)
        self.assertEqual(self.elero_device._response['header'], None)
        self.assertEqual(self.elero_device._response['length'], None)
        self.assertEqual(self.elero_device._response['command'], None)
        self.assertEqual(self.elero_device._response['ch_h'], None)
        self.assertEqual(self.elero_device._response['ch_l'], None)
        self.assertEqual(self.elero_device._response['chs'], set())
        self.assertEqual(self.elero_device._response['status'], None)
        self.assertEqual(self.elero_device._response['cs'], None)

    def test_get_check_command(self):
        """Testing the CHECK command."""
        self.assertEqual(self.elero_device._get_check_command(),
                         [elero_platform.BYTE_HEADER,
                          elero_platform.BYTE_LENGTH_2,
                          elero_platform.COMMAND_CHECK])

    def test_get_info_command(self):
        """Testing the INFO command."""
        self.assertEqual(self.elero_device._get_info_command(),
                         [elero_platform.BYTE_HEADER,
                          elero_platform.BYTE_LENGTH_4,
                          elero_platform.COMMAND_INFO,
                          0, 1])

    def test_get_up_command(self):
        """Testing the UP command."""
        self.assertEqual(self.elero_device._get_up_command(),
                         [elero_platform.BYTE_HEADER,
                          elero_platform.BYTE_LENGTH_5,
                          elero_platform.COMMAND_SEND,
                          0, 1,
                          elero_platform.PAYLOAD_UP])

    def test_get_down_command(self):
        """Testing the DOWN command."""
        self.assertEqual(self.elero_device._get_down_command(),
                         [elero_platform.BYTE_HEADER,
                          elero_platform.BYTE_LENGTH_5,
                          elero_platform.COMMAND_SEND,
                          0, 1,
                          elero_platform.PAYLOAD_DOWN])

    def test_get_stop_command(self):
        """Testing the STOP command."""
        self.assertEqual(self.elero_device._get_stop_command(),
                         [elero_platform.BYTE_HEADER,
                          elero_platform.BYTE_LENGTH_5,
                          elero_platform.COMMAND_SEND,
                          0, 1,
                          elero_platform.PAYLOAD_STOP])

    def test_get_intermediate_command(self):
        """Testing the INTERMEDIATE command."""
        self.assertEqual(self.elero_device._get_intermediate_command(),
                         [elero_platform.BYTE_HEADER,
                          elero_platform.BYTE_LENGTH_5,
                          elero_platform.COMMAND_SEND,
                          0, 1,
                          elero_platform.PAYLOAD_INTERMEDIATE_POS])

    def test_get_ventilation_tilting_command(self):
        """Testing the VENTILATION command."""
        self.assertEqual(self.elero_device._get_ventilation_tilting_command(),
                         [elero_platform.BYTE_HEADER,
                          elero_platform.BYTE_LENGTH_5,
                          elero_platform.COMMAND_SEND,
                          0, 1,
                          elero_platform.PAYLOAD_VENTILATION_POS_TILTING])

    def test_parse_response_with_no_response(self):
        """Testing the parse_response method."""
        # No response or serial data
        ser_resp = b''
        self.assertEqual(self.elero_device._parse_response(ser_resp), None)
        self.assertEqual(self.elero_device._response['bytes'],
                         elero_platform.NO_SERIAL_RESPONSE)
        self.assertEqual(self.elero_device._response['header'], None)
        self.assertEqual(self.elero_device._response['length'], None)
        self.assertEqual(self.elero_device._response['command'], None)
        self.assertEqual(self.elero_device._response['ch_h'], None)
        self.assertEqual(self.elero_device._response['ch_l'], None)
        self.assertEqual(self.elero_device._response['chs'], set())
        self.assertEqual(self.elero_device._response['status'],
                         elero_platform.INFO_NO_INFORMATION)
        self.assertEqual(self.elero_device._response['cs'], None)

    def test_parse_response_easy_check_123467(self):
        """Testing the parse_response method."""
        # Common and Easy Confirmed (the answer on Easy Check) - 1,2,3,4,6,7
        ser_resp = b'\xAA\x04\x4B\x00\x6F\x98'
        self.assertEqual(self.elero_device._parse_response(ser_resp), None)
        self.assertEqual(self.elero_device._response['bytes'], ser_resp)
        self.assertEqual(self.elero_device._response['header'], 170)
        self.assertEqual(self.elero_device._response['length'], 4)
        self.assertEqual(self.elero_device._response['command'], 75)
        self.assertEqual(self.elero_device._response['ch_h'], ())
        self.assertEqual(self.elero_device._response['ch_l'],
                         (1, 2, 3, 4, 6, 7))
        self.assertEqual(self.elero_device._response['chs'],
                         {1, 2, 3, 4, 6, 7})
        self.assertEqual(self.elero_device._response['status'],
                         elero_platform.INFO_UNKNOWN)
        self.assertEqual(self.elero_device._response['cs'], 152)

    def test_parse_response_easy_info_andy_01(self):
        """Testing the parse_response method."""
        # Easy Ack (the answer on Easy Info) - 11
        ser_resp = b'\xaa\x05M\x04\x00\x01\xff'
        self.assertEqual(self.elero_device._parse_response(ser_resp), None)
        self.assertEqual(self.elero_device._response['bytes'], ser_resp)
        self.assertEqual(self.elero_device._response['header'], 170)
        self.assertEqual(self.elero_device._response['length'], 5)
        self.assertEqual(self.elero_device._response['command'], 77)
        self.assertEqual(self.elero_device._response['ch_h'], (11,))
        self.assertEqual(self.elero_device._response['ch_l'], ())
        self.assertEqual(self.elero_device._response['chs'], {11})
        self.assertEqual(self.elero_device._response['status'],
                         elero_platform.INFO_TOP_POSITION_STOP)
        self.assertEqual(self.elero_device._response['cs'], 255)

    def test_parse_response_easy_info_1(self):
        """Testing the parse_response method."""
        # Easy Ack (the answer on Easy Info) - 1
        ser_resp = b'\xAA\x05\x4D\x00\x01\x00\x03'
        self.assertEqual(self.elero_device._parse_response(ser_resp), None)
        self.assertEqual(self.elero_device._response['bytes'], ser_resp)
        self.assertEqual(self.elero_device._response['header'], 170)
        self.assertEqual(self.elero_device._response['length'], 5)
        self.assertEqual(self.elero_device._response['command'], 77)
        self.assertEqual(self.elero_device._response['ch_h'], ())
        self.assertEqual(self.elero_device._response['ch_l'], (1,))
        self.assertEqual(self.elero_device._response['chs'], {1})
        self.assertEqual(self.elero_device._response['status'],
                         elero_platform.INFO_NO_INFORMATION)
        self.assertEqual(self.elero_device._response['cs'], 3)

    def test_parse_response_easy_info_7(self):
        """Testing the parse_response method."""
        # Easy Ack (the answer on Easy Info) - 7
        ser_resp = b'\xAA\x05\x4D\x00\x40\x00\xC4'
        self.assertEqual(
            self.elero_device._parse_response(ser_resp), None)
        self.assertEqual(
            self.elero_device._response['bytes'], ser_resp)
        self.assertEqual(self.elero_device._response['header'], 170)
        self.assertEqual(self.elero_device._response['length'], 5)
        self.assertEqual(self.elero_device._response['command'], 77)
        self.assertEqual(self.elero_device._response['ch_h'], ())
        self.assertEqual(self.elero_device._response['ch_l'], (7,))
        self.assertEqual(self.elero_device._response['chs'], {7})
        self.assertEqual(self.elero_device._response['status'],
                         elero_platform.INFO_NO_INFORMATION)
        self.assertEqual(self.elero_device._response['cs'], 196)

    def test_parse_response_unknown(self):
        """Testing the parse_response method."""
        # unknown info status - 7
        ser_resp = b'\xAA\x05\x4D\x00\x40\x12\xb7'
        self.assertEqual(self.elero_device._parse_response(ser_resp), None)
        self.assertEqual(self.elero_device._response['bytes'], ser_resp)
        self.assertEqual(self.elero_device._response['header'], 170)
        self.assertEqual(self.elero_device._response['length'], 5)
        self.assertEqual(self.elero_device._response['command'], 77)
        self.assertEqual(self.elero_device._response['ch_h'], ())
        self.assertEqual(self.elero_device._response['ch_l'], (7,))
        self.assertEqual(self.elero_device._response['chs'], {7})
        self.assertEqual(self.elero_device._response['status'],
                         elero_platform.INFO_UNKNOWN)
        self.assertEqual(self.elero_device._response['cs'], 183)

    def test_parse_response_else(self):
        """Testing the parse_response method."""
        # main else
        ser_resp = b'\xAA\xAA\xAA\x00\x00\xAA\xAA\xAA\xAA'
        self.assertEqual(self.elero_device._parse_response(ser_resp), None)
        self.assertEqual(self.elero_device._response['bytes'], ser_resp)
        self.assertEqual(self.elero_device._response['header'], 170)
        self.assertEqual(self.elero_device._response['length'], 170)
        self.assertEqual(self.elero_device._response['command'], 170)
        self.assertEqual(self.elero_device._response['ch_h'], ())
        self.assertEqual(self.elero_device._response['ch_l'], ())
        self.assertEqual(self.elero_device._response['chs'], set())
        self.assertEqual(self.elero_device._response['status'],
                         elero_platform.INFO_UNKNOWN)
        self.assertEqual(self.elero_device._response['cs'], 170)

    def test_calculate_checksum(self):
        """Testing the _calculate_checksum method."""
        # b'\xAA\x04\x4B\x00\x6F\x98'
        self.assertEqual(self.elero_device._calculate_checksum(
            0xAA, 0x04, 0x4B, 0x00, 0x6F), 0x98)
        # b'\xAA\x05\x4D\x00\x40\x02\xC2'
        self.assertEqual(self.elero_device._calculate_checksum(
            0xAA, 0x05, 0x4D, 0x00, 0x40, 0x02), 0xC2)
        # b'\xAA\x04\x4E\x00\x04\x00'
        self.assertEqual(self.elero_device._calculate_checksum(
            0xAA, 0x04, 0x4E, 0x00, 0x04), 0x00)
        # b'\xAA\x04\x4E\x00\x10\xF4'
        self.assertEqual(self.elero_device._calculate_checksum(
            0xAA, 0x04, 0x4E, 0x00, 0x10), 0xF4)

    def test_create_serial_data(self):
        """Testing the _create_serial_data method."""
        self.assertEqual(self.elero_device._create_serial_data(
            [0xAA, 0x04, 0x4B, 0x00, 0x6F, 0x98]),
            b'\xAA\x04\x4B\x00\x6F\x98')

    def test_set_channel_bits(self):
        """Testing the channel bit seting.

        The the _set_upper_channel_bits and
        the _set_lower_channel_bits method.
        """
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 0x00)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x01)

    def test_set_channel_bits_all(self):
        """Testing the channel bit seting based on predefined channel.

        The the _set_upper_channel_bits and
        the _set_lower_channel_bits method.
        """
        self.elero_device._channels = (1,)
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 0x00)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x01)
        self.elero_device._channels = (2,)
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 0x00)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x02)
        self.elero_device._channels = (3,)
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 0x00)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x04)
        self.elero_device._channels = (4,)
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 0x00)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x08)
        self.elero_device._channels = (5,)
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 0x00)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x10)
        self.elero_device._channels = (6,)
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 0x00)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x20)
        self.elero_device._channels = (7,)
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 0x00)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x40)
        self.elero_device._channels = (8,)
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 0x00)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x80)
        self.elero_device._channels = (9,)
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 0x01)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x00)
        self.elero_device._channels = (10,)
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 0x02)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x00)
        self.elero_device._channels = (11,)
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 0x04)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x00)
        self.elero_device._channels = (12,)
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 0x08)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x00)
        self.elero_device._channels = (13,)
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 0x10)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x00)
        self.elero_device._channels = (14,)
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 0x20)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x00)
        self.elero_device._channels = (15,)
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 0x40)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x00)
        self.elero_device._channels = (16,)
        self.assertEqual(self.elero_device._set_upper_channel_bits(), 128)
        self.assertEqual(self.elero_device._set_lower_channel_bits(), 0x00)

    def test_get_learned_channels(self):
        """Testing the _get_learned_channels method."""
        self.assertEqual(self.elero_device._get_learned_channels(0x00),
                         ())
        self.assertEqual(self.elero_device._get_learned_channels(0x01),
                         (1,))
        self.assertEqual(self.elero_device._get_learned_channels(0x02),
                         (2,))
        self.assertEqual(self.elero_device._get_learned_channels(0x03),
                         (1, 2))
        self.assertEqual(self.elero_device._get_learned_channels(0x04),
                         (3,))
        self.assertEqual(self.elero_device._get_learned_channels(0x05),
                         (1, 3))
        self.assertEqual(self.elero_device._get_learned_channels(0x06),
                         (2, 3))
        self.assertEqual(self.elero_device._get_learned_channels(0x07),
                         (1, 2, 3))
        self.assertEqual(self.elero_device._get_learned_channels(0x08),
                         (4,))
        self.assertEqual(self.elero_device._get_learned_channels(0x09),
                         (1, 4))
        self.assertEqual(self.elero_device._get_learned_channels(0x0A),
                         (2, 4))
        self.assertEqual(self.elero_device._get_learned_channels(0x0B),
                         (1, 2, 4))
        self.assertEqual(self.elero_device._get_learned_channels(0x0C),
                         (3, 4))
        self.assertEqual(self.elero_device._get_learned_channels(0x0D),
                         (1, 3, 4))
        self.assertEqual(self.elero_device._get_learned_channels(0x0E),
                         (2, 3, 4))
        self.assertEqual(self.elero_device._get_learned_channels(0x0F),
                         (1, 2, 3, 4))
        self.assertEqual(self.elero_device._get_learned_channels(0x10),
                         (5,))
        self.assertEqual(self.elero_device._get_learned_channels(0x11),
                         (1, 5))
        self.assertEqual(self.elero_device._get_learned_channels(0x12),
                         (2, 5))
        self.assertEqual(self.elero_device._get_learned_channels(0x13),
                         (1, 2, 5))
        self.assertEqual(self.elero_device._get_learned_channels(0x14),
                         (3, 5))
        self.assertEqual(self.elero_device._get_learned_channels(0x15),
                         (1, 3, 5))
        self.assertEqual(self.elero_device._get_learned_channels(0x16),
                         (2, 3, 5))
        self.assertEqual(self.elero_device._get_learned_channels(0x17),
                         (1, 2, 3, 5))
        self.assertEqual(self.elero_device._get_learned_channels(0x18),
                         (4, 5))
        self.assertEqual(self.elero_device._get_learned_channels(0x19),
                         (1, 4, 5))
        self.assertEqual(self.elero_device._get_learned_channels(0x1A),
                         (2, 4, 5))
        self.assertEqual(self.elero_device._get_learned_channels(0x1B),
                         (1, 2, 4, 5))
        self.assertEqual(self.elero_device._get_learned_channels(0x1C),
                         (3, 4, 5))
        self.assertEqual(self.elero_device._get_learned_channels(0x1D),
                         (1, 3, 4, 5))
        self.assertEqual(self.elero_device._get_learned_channels(0x1E),
                         (2, 3, 4, 5))
        self.assertEqual(self.elero_device._get_learned_channels(0x1F),
                         (1, 2, 3, 4, 5))
        self.assertEqual(self.elero_device._get_learned_channels(0x20),
                         (6,))
        self.assertEqual(self.elero_device._get_learned_channels(0x21),
                         (1, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x22),
                         (2, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x23),
                         (1, 2, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x24),
                         (3, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x25),
                         (1, 3, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x26),
                         (2, 3, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x27),
                         (1, 2, 3, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x28),
                         (4, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x29),
                         (1, 4, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x2A),
                         (2, 4, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x2B),
                         (1, 2, 4, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x2C),
                         (3, 4, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x2D),
                         (1, 3, 4, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x2E),
                         (2, 3, 4, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x2F),
                         (1, 2, 3, 4, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x30),
                         (5, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x31),
                         (1, 5, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x32),
                         (2, 5, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x33),
                         (1, 2, 5, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x34),
                         (3, 5, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x35),
                         (1, 3, 5, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x36),
                         (2, 3, 5, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x37),
                         (1, 2, 3, 5, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x38),
                         (4, 5, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x39),
                         (1, 4, 5, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x3A),
                         (2, 4, 5, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x3B),
                         (1, 2, 4, 5, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x3C),
                         (3, 4, 5, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x3D),
                         (1, 3, 4, 5, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x3E),
                         (2, 3, 4, 5, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x3F),
                         (1, 2, 3, 4, 5, 6))
        self.assertEqual(self.elero_device._get_learned_channels(0x40),
                         (7,))
        self.assertEqual(self.elero_device._get_learned_channels(0x41),
                         (1, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x42),
                         (2, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x43),
                         (1, 2, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x44),
                         (3, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x45),
                         (1, 3, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x46),
                         (2, 3, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x47),
                         (1, 2, 3, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x48),
                         (4, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x49),
                         (1, 4, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x4A),
                         (2, 4, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x4B),
                         (1, 2, 4, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x4C),
                         (3, 4, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x4D),
                         (1, 3, 4, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x4E),
                         (2, 3, 4, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x4F),
                         (1, 2, 3, 4, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x50),
                         (5, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x51),
                         (1, 5, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x52),
                         (2, 5, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x53),
                         (1, 2, 5, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x54),
                         (3, 5, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x55),
                         (1, 3, 5, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x56),
                         (2, 3, 5, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x57),
                         (1, 2, 3, 5, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x58),
                         (4, 5, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x59),
                         (1, 4, 5, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x5A),
                         (2, 4, 5, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x5B),
                         (1, 2, 4, 5, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x5C),
                         (3, 4, 5, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x5D),
                         (1, 3, 4, 5, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x5E),
                         (2, 3, 4, 5, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x5F),
                         (1, 2, 3, 4, 5, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x60),
                         (6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x61),
                         (1, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x62),
                         (2, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x63),
                         (1, 2, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x64),
                         (3, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x65),
                         (1, 3, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x66),
                         (2, 3, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x67),
                         (1, 2, 3, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x68),
                         (4, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x69),
                         (1, 4, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x6A),
                         (2, 4, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x6B),
                         (1, 2, 4, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x6C),
                         (3, 4, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x6D),
                         (1, 3, 4, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x6E),
                         (2, 3, 4, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x6F),
                         (1, 2, 3, 4, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x70),
                         (5, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x71),
                         (1, 5, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x72),
                         (2, 5, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x73),
                         (1, 2, 5, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x74),
                         (3, 5, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x75),
                         (1, 3, 5, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x76),
                         (2, 3, 5, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x77),
                         (1, 2, 3, 5, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x78),
                         (4, 5, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x79),
                         (1, 4, 5, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x7A),
                         (2, 4, 5, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x7B),
                         (1, 2, 4, 5, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x7C),
                         (3, 4, 5, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x7D),
                         (1, 3, 4, 5, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x7E),
                         (2, 3, 4, 5, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x7F),
                         (1, 2, 3, 4, 5, 6, 7))
        self.assertEqual(self.elero_device._get_learned_channels(0x80),
                         (8,))
        self.assertEqual(self.elero_device._get_learned_channels(0x81),
                         (1, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x82),
                         (2, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x83),
                         (1, 2, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x84),
                         (3, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x85),
                         (1, 3, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x86),
                         (2, 3, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x87),
                         (1, 2, 3, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x88),
                         (4, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x89),
                         (1, 4, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x8A),
                         (2, 4, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x8B),
                         (1, 2, 4, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x8C),
                         (3, 4, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x8D),
                         (1, 3, 4, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x8E),
                         (2, 3, 4, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x8F),
                         (1, 2, 3, 4, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x90),
                         (5, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x91),
                         (1, 5, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x92),
                         (2, 5, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x93),
                         (1, 2, 5, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x94),
                         (3, 5, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x95),
                         (1, 3, 5, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x96),
                         (2, 3, 5, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x97),
                         (1, 2, 3, 5, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x98),
                         (4, 5, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x99),
                         (1, 4, 5, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x9A),
                         (2, 4, 5, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x9B),
                         (1, 2, 4, 5, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x9C),
                         (3, 4, 5, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x9D),
                         (1, 3, 4, 5, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x9E),
                         (2, 3, 4, 5, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x9F),
                         (1, 2, 3, 4, 5, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xA0),
                         (6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xA1),
                         (1, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xA2),
                         (2, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xA3),
                         (1, 2, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xA4),
                         (3, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xA5),
                         (1, 3, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xA6),
                         (2, 3, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xA7),
                         (1, 2, 3, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xA8),
                         (4, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xA9),
                         (1, 4, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xAA),
                         (2, 4, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xAB),
                         (1, 2, 4, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xAC),
                         (3, 4, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xAD),
                         (1, 3, 4, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xAE),
                         (2, 3, 4, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xAF),
                         (1, 2, 3, 4, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xB0),
                         (5, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xB1),
                         (1, 5, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xB2),
                         (2, 5, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xB3),
                         (1, 2, 5, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xB4),
                         (3, 5, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xB5),
                         (1, 3, 5, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xB6),
                         (2, 3, 5, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xB7),
                         (1, 2, 3, 5, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xB8),
                         (4, 5, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xB9),
                         (1, 4, 5, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xBA),
                         (2, 4, 5, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xBB),
                         (1, 2, 4, 5, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xBC),
                         (3, 4, 5, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xBD),
                         (1, 3, 4, 5, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xBE),
                         (2, 3, 4, 5, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xBF),
                         (1, 2, 3, 4, 5, 6, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xC0),
                         (7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xC1),
                         (1, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xC2),
                         (2, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xC3),
                         (1, 2, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xC4),
                         (3, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xC5),
                         (1, 3, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xC6),
                         (2, 3, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xC7),
                         (1, 2, 3, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xC8),
                         (4, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xC9),
                         (1, 4, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xCA),
                         (2, 4, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xCB),
                         (1, 2, 4, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xCC),
                         (3, 4, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xCD),
                         (1, 3, 4, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xCE),
                         (2, 3, 4, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xCF),
                         (1, 2, 3, 4, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xD0),
                         (5, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xD1),
                         (1, 5, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xD2),
                         (2, 5, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xD3),
                         (1, 2, 5, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xD4),
                         (3, 5, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xD5),
                         (1, 3, 5, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xD6),
                         (2, 3, 5, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xD7),
                         (1, 2, 3, 5, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xD8),
                         (4, 5, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xD9),
                         (1, 4, 5, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xDA),
                         (2, 4, 5, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xDB),
                         (1, 2, 4, 5, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xDC),
                         (3, 4, 5, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xDD),
                         (1, 3, 4, 5, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xDE),
                         (2, 3, 4, 5, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xDF),
                         (1, 2, 3, 4, 5, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xE0),
                         (6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xE1),
                         (1, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xE2),
                         (2, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xE3),
                         (1, 2, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xE4),
                         (3, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xE5),
                         (1, 3, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xE6),
                         (2, 3, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xE7),
                         (1, 2, 3, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xE8),
                         (4, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xE9),
                         (1, 4, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xEA),
                         (2, 4, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xEB),
                         (1, 2, 4, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xEC),
                         (3, 4, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xED),
                         (1, 3, 4, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xEE),
                         (2, 3, 4, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xEF),
                         (1, 2, 3, 4, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xF0),
                         (5, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xF1),
                         (1, 5, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xF2),
                         (2, 5, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xF3),
                         (1, 2, 5, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xF4),
                         (3, 5, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xF5),
                         (1, 3, 5, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xF6),
                         (2, 3, 5, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xF7),
                         (1, 2, 3, 5, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xF8),
                         (4, 5, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xF9),
                         (1, 4, 5, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xFA),
                         (2, 4, 5, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xFB),
                         (1, 2, 4, 5, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xFC),
                         (3, 4, 5, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xFD),
                         (1, 3, 4, 5, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xFE),
                         (2, 3, 4, 5, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0xFF),
                         (1, 2, 3, 4, 5, 6, 7, 8))
        self.assertEqual(self.elero_device._get_learned_channels(0x100),
                         (9,))
        self.assertEqual(self.elero_device._get_learned_channels(0x300),
                         (9, 10))
        self.assertEqual(self.elero_device._get_learned_channels(0x400),
                         (11,))
        self.assertEqual(self.elero_device._get_learned_channels(0x401),
                         (1, 11))

    def test_get_upper_channel_bits(self):
        """Testing the _create_serial_data method."""
        # ch: 1
        resp = b'\xaa\x04N\x00\x01\x02'
        self.assertEqual(self.elero_device._get_upper_channel_bits(
            resp[3]), ())
        self.assertEqual(self.elero_device._get_lower_channel_bits(
            resp[4]), (1, ))
        # ch: 10
        resp = b'\xaa\x04N\x02\x00\x02'
        self.assertEqual(self.elero_device._get_upper_channel_bits(
            resp[3]), (10,))
        self.assertEqual(self.elero_device._get_lower_channel_bits(
            resp[4]), ())
        # ch: 12
        resp = b'\xaa\x05M\x08\x00\x01\xfb'
        self.assertEqual(self.elero_device._get_upper_channel_bits(
            resp[3]), (12,))
        self.assertEqual(self.elero_device._get_lower_channel_bits(
            resp[4]), ())
        # ch: 13
        resp = b'\xaa\x05M\x10\x00\x01\xf3'
        self.assertEqual(self.elero_device._get_upper_channel_bits(
            resp[3]), (13,))
        self.assertEqual(self.elero_device._get_lower_channel_bits(
            resp[4]), ())

    def test_verify_channel_same(self):
        """Testing the _create_serial_data method."""
        self.test_parse_response_easy_info_1()
        self.assertEqual(self.elero_device._verify_channels(), True)

    def test_verify_channel_not_same(self):
        """Testing the _create_serial_data method."""
        self.test_parse_response_easy_info_7()
        self.assertEqual(self.elero_device._verify_channels(), False)


if __name__ == '__main__':
    unittest.main()
