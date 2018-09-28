# -*- coding: utf-8 -*-
"""
Elero Unittest.

Unittesting the Elero lib.
"""
import unittest
from unittest.mock import Mock

from custom_components import elero as elero_component
from custom_components.cover import elero as elero_platform


class EleroUnittest(unittest.TestCase):
    """Unittest to Elero."""

    def setUp(self):
        """Seting up the unittest."""
        self.port = Mock()
        self.transmitter = elero_component.EleroTransmitter(self.port,
                                                            100, 2, 100)
        self.cover_device = elero_component.EleroDevice(1)

    def test_check(self):
        """Testing the CHECK command.

        self.port.read = Mock(return_value="my string")

        self.assertEqual(self.transmitter.serial_read(6), "my string")
        """
        pass

    def test_info(self):
        """Testing the INFO command."""
        pass

    def test_up(self):
        """Testing the UP command."""
        pass

    def test_down(self):
        """Testing the DOWN command."""
        pass

    def test_stop(self):
        """Testing the STOP command."""
        pass

    def test_intermediate(self):
        """Testing the INTERMEDIATE command."""
        pass

    def test_tilt(self):
        """Testing the TILT command."""
        pass

    def test_ventilation(self):
        """Testing the VENTILATION command."""
        pass

    def test_get_response(self):
        """Testing the _get_response method."""
        pass

    def test_send_command(self):
        """Testing the _send_command method."""
        m = Mock()
        m._send_command = Mock(return_value="my string")
        self.assertEqual(m._send_command, "my strin")

    def test_calculate_checksum(self):
        """Testing the _calculate_checksum method."""
        # b'\xAA\x04\x4B\x00\x6F\x98'
        self.assertEqual(self.cover_device._calculate_checksum(
            0xAA, 0x04, 0x4B, 0x00, 0x6F), 0x98)
        # b'\xAA\x05\x4D\x00\x40\x02\xC2'
        self.assertEqual(self.cover_device._calculate_checksum(
            0xAA, 0x05, 0x4D, 0x00, 0x40, 0x02), 0xC2)
        # b'\xAA\x04\x4E\x00\x04\x00'
        self.assertEqual(self.cover_device._calculate_checksum(
            0xAA, 0x04, 0x4E, 0x00, 0x04), 0x00)
        # b'\xAA\x04\x4E\x00\x10\xF4'
        self.assertEqual(self.cover_device._calculate_checksum(
            0xAA, 0x04, 0x4E, 0x00, 0x10), 0xF4)

    def test_set_channel_bits(self):
        """Testing the channel bit seting.

        The the _get_upper_channel_bits and
        the _get_lower_channel_bits method.
        """
        self.assertEqual(self.cover_device._get_upper_channel_bits(1), 0x00)
        self.assertEqual(self.cover_device._get_lower_channel_bits(1), 0x01)
        self.assertEqual(self.cover_device._get_upper_channel_bits(2), 0x00)
        self.assertEqual(self.cover_device._get_lower_channel_bits(2), 0x02)
        self.assertEqual(self.cover_device._get_upper_channel_bits(3), 0x00)
        self.assertEqual(self.cover_device._get_lower_channel_bits(3), 0x04)
        self.assertEqual(self.cover_device._get_upper_channel_bits(4), 0x00)
        self.assertEqual(self.cover_device._get_lower_channel_bits(4), 0x08)
        self.assertEqual(self.cover_device._get_upper_channel_bits(5), 0x00)
        self.assertEqual(self.cover_device._get_lower_channel_bits(5), 0x10)
        self.assertEqual(self.cover_device._get_upper_channel_bits(6), 0x00)
        self.assertEqual(self.cover_device._get_lower_channel_bits(6), 0x20)
        self.assertEqual(self.cover_device._get_upper_channel_bits(7), 0x00)
        self.assertEqual(self.cover_device._get_lower_channel_bits(7), 0x40)
        self.assertEqual(self.cover_device._get_upper_channel_bits(8), 0x00)
        self.assertEqual(self.cover_device._get_lower_channel_bits(8), 0x80)
        self.assertEqual(self.cover_device._get_upper_channel_bits(9), 0x01)
        self.assertEqual(self.cover_device._get_lower_channel_bits(9), 0x00)
        self.assertEqual(self.cover_device._get_upper_channel_bits(10), 0x02)
        self.assertEqual(self.cover_device._get_lower_channel_bits(10), 0x00)
        self.assertEqual(self.cover_device._get_upper_channel_bits(11), 0x04)
        self.assertEqual(self.cover_device._get_lower_channel_bits(11), 0x00)
        self.assertEqual(self.cover_device._get_upper_channel_bits(12), 0x08)
        self.assertEqual(self.cover_device._get_lower_channel_bits(12), 0x00)
        self.assertEqual(self.cover_device._get_upper_channel_bits(13), 0x10)
        self.assertEqual(self.cover_device._get_lower_channel_bits(13), 0x00)
        self.assertEqual(self.cover_device._get_upper_channel_bits(14), 0x20)
        self.assertEqual(self.cover_device._get_lower_channel_bits(14), 0x00)
        self.assertEqual(self.cover_device._get_upper_channel_bits(15), 0x40)
        self.assertEqual(self.cover_device._get_lower_channel_bits(15), 0x00)
        self.assertEqual(self.cover_device._get_upper_channel_bits(16), 128)
        self.assertEqual(self.cover_device._get_lower_channel_bits(16), 0x00)

    def test_get_channels_from_response(self):
        """Testing the _get_channels_from_response method."""
        self.assertEqual(self.cover_device._get_channels_from_response(0x00),
                         ())
        self.assertEqual(self.cover_device._get_channels_from_response(0x01),
                         (1,))
        self.assertEqual(self.cover_device._get_channels_from_response(0x02),
                         (2,))
        self.assertEqual(self.cover_device._get_channels_from_response(0x03),
                         (1, 2))
        self.assertEqual(self.cover_device._get_channels_from_response(0x04),
                         (3,))
        self.assertEqual(self.cover_device._get_channels_from_response(0x05),
                         (1, 3))
        self.assertEqual(self.cover_device._get_channels_from_response(0x06),
                         (2, 3))
        self.assertEqual(self.cover_device._get_channels_from_response(0x07),
                         (1, 2, 3))
        self.assertEqual(self.cover_device._get_channels_from_response(0x08),
                         (4,))
        self.assertEqual(self.cover_device._get_channels_from_response(0x09),
                         (1, 4))
        self.assertEqual(self.cover_device._get_channels_from_response(0x0A),
                         (2, 4))
        self.assertEqual(self.cover_device._get_channels_from_response(0x0B),
                         (1, 2, 4))
        self.assertEqual(self.cover_device._get_channels_from_response(0x0C),
                         (3, 4))
        self.assertEqual(self.cover_device._get_channels_from_response(0x0D),
                         (1, 3, 4))
        self.assertEqual(self.cover_device._get_channels_from_response(0x0E),
                         (2, 3, 4))
        self.assertEqual(self.cover_device._get_channels_from_response(0x0F),
                         (1, 2, 3, 4))
        self.assertEqual(self.cover_device._get_channels_from_response(0x10),
                         (5,))
        self.assertEqual(self.cover_device._get_channels_from_response(0x11),
                         (1, 5))
        self.assertEqual(self.cover_device._get_channels_from_response(0x12),
                         (2, 5))
        self.assertEqual(self.cover_device._get_channels_from_response(0x13),
                         (1, 2, 5))
        self.assertEqual(self.cover_device._get_channels_from_response(0x14),
                         (3, 5))
        self.assertEqual(self.cover_device._get_channels_from_response(0x15),
                         (1, 3, 5))
        self.assertEqual(self.cover_device._get_channels_from_response(0x16),
                         (2, 3, 5))
        self.assertEqual(self.cover_device._get_channels_from_response(0x17),
                         (1, 2, 3, 5))
        self.assertEqual(self.cover_device._get_channels_from_response(0x18),
                         (4, 5))
        self.assertEqual(self.cover_device._get_channels_from_response(0x19),
                         (1, 4, 5))
        self.assertEqual(self.cover_device._get_channels_from_response(0x1A),
                         (2, 4, 5))
        self.assertEqual(self.cover_device._get_channels_from_response(0x1B),
                         (1, 2, 4, 5))
        self.assertEqual(self.cover_device._get_channels_from_response(0x1C),
                         (3, 4, 5))
        self.assertEqual(self.cover_device._get_channels_from_response(0x1D),
                         (1, 3, 4, 5))
        self.assertEqual(self.cover_device._get_channels_from_response(0x1E),
                         (2, 3, 4, 5))
        self.assertEqual(self.cover_device._get_channels_from_response(0x1F),
                         (1, 2, 3, 4, 5))
        self.assertEqual(self.cover_device._get_channels_from_response(0x20),
                         (6,))
        self.assertEqual(self.cover_device._get_channels_from_response(0x21),
                         (1, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x22),
                         (2, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x23),
                         (1, 2, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x24),
                         (3, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x25),
                         (1, 3, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x26),
                         (2, 3, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x27),
                         (1, 2, 3, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x28),
                         (4, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x29),
                         (1, 4, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x2A),
                         (2, 4, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x2B),
                         (1, 2, 4, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x2C),
                         (3, 4, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x2D),
                         (1, 3, 4, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x2E),
                         (2, 3, 4, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x2F),
                         (1, 2, 3, 4, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x30),
                         (5, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x31),
                         (1, 5, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x32),
                         (2, 5, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x33),
                         (1, 2, 5, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x34),
                         (3, 5, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x35),
                         (1, 3, 5, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x36),
                         (2, 3, 5, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x37),
                         (1, 2, 3, 5, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x38),
                         (4, 5, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x39),
                         (1, 4, 5, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x3A),
                         (2, 4, 5, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x3B),
                         (1, 2, 4, 5, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x3C),
                         (3, 4, 5, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x3D),
                         (1, 3, 4, 5, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x3E),
                         (2, 3, 4, 5, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x3F),
                         (1, 2, 3, 4, 5, 6))
        self.assertEqual(self.cover_device._get_channels_from_response(0x40),
                         (7,))
        self.assertEqual(self.cover_device._get_channels_from_response(0x41),
                         (1, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x42),
                         (2, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x43),
                         (1, 2, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x44),
                         (3, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x45),
                         (1, 3, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x46),
                         (2, 3, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x47),
                         (1, 2, 3, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x48),
                         (4, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x49),
                         (1, 4, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x4A),
                         (2, 4, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x4B),
                         (1, 2, 4, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x4C),
                         (3, 4, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x4D),
                         (1, 3, 4, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x4E),
                         (2, 3, 4, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x4F),
                         (1, 2, 3, 4, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x50),
                         (5, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x51),
                         (1, 5, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x52),
                         (2, 5, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x53),
                         (1, 2, 5, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x54),
                         (3, 5, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x55),
                         (1, 3, 5, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x56),
                         (2, 3, 5, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x57),
                         (1, 2, 3, 5, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x58),
                         (4, 5, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x59),
                         (1, 4, 5, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x5A),
                         (2, 4, 5, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x5B),
                         (1, 2, 4, 5, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x5C),
                         (3, 4, 5, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x5D),
                         (1, 3, 4, 5, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x5E),
                         (2, 3, 4, 5, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x5F),
                         (1, 2, 3, 4, 5, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x60),
                         (6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x61),
                         (1, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x62),
                         (2, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x63),
                         (1, 2, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x64),
                         (3, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x65),
                         (1, 3, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x66),
                         (2, 3, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x67),
                         (1, 2, 3, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x68),
                         (4, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x69),
                         (1, 4, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x6A),
                         (2, 4, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x6B),
                         (1, 2, 4, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x6C),
                         (3, 4, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x6D),
                         (1, 3, 4, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x6E),
                         (2, 3, 4, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x6F),
                         (1, 2, 3, 4, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x70),
                         (5, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x71),
                         (1, 5, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x72),
                         (2, 5, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x73),
                         (1, 2, 5, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x74),
                         (3, 5, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x75),
                         (1, 3, 5, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x76),
                         (2, 3, 5, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x77),
                         (1, 2, 3, 5, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x78),
                         (4, 5, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x79),
                         (1, 4, 5, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x7A),
                         (2, 4, 5, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x7B),
                         (1, 2, 4, 5, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x7C),
                         (3, 4, 5, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x7D),
                         (1, 3, 4, 5, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x7E),
                         (2, 3, 4, 5, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x7F),
                         (1, 2, 3, 4, 5, 6, 7))
        self.assertEqual(self.cover_device._get_channels_from_response(0x80),
                         (8,))
        self.assertEqual(self.cover_device._get_channels_from_response(0x81),
                         (1, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x82),
                         (2, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x83),
                         (1, 2, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x84),
                         (3, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x85),
                         (1, 3, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x86),
                         (2, 3, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x87),
                         (1, 2, 3, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x88),
                         (4, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x89),
                         (1, 4, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x8A),
                         (2, 4, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x8B),
                         (1, 2, 4, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x8C),
                         (3, 4, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x8D),
                         (1, 3, 4, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x8E),
                         (2, 3, 4, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x8F),
                         (1, 2, 3, 4, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x90),
                         (5, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x91),
                         (1, 5, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x92),
                         (2, 5, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x93),
                         (1, 2, 5, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x94),
                         (3, 5, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x95),
                         (1, 3, 5, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x96),
                         (2, 3, 5, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x97),
                         (1, 2, 3, 5, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x98),
                         (4, 5, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x99),
                         (1, 4, 5, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x9A),
                         (2, 4, 5, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x9B),
                         (1, 2, 4, 5, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x9C),
                         (3, 4, 5, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x9D),
                         (1, 3, 4, 5, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x9E),
                         (2, 3, 4, 5, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x9F),
                         (1, 2, 3, 4, 5, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xA0),
                         (6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xA1),
                         (1, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xA2),
                         (2, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xA3),
                         (1, 2, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xA4),
                         (3, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xA5),
                         (1, 3, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xA6),
                         (2, 3, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xA7),
                         (1, 2, 3, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xA8),
                         (4, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xA9),
                         (1, 4, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xAA),
                         (2, 4, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xAB),
                         (1, 2, 4, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xAC),
                         (3, 4, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xAD),
                         (1, 3, 4, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xAE),
                         (2, 3, 4, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xAF),
                         (1, 2, 3, 4, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xB0),
                         (5, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xB1),
                         (1, 5, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xB2),
                         (2, 5, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xB3),
                         (1, 2, 5, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xB4),
                         (3, 5, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xB5),
                         (1, 3, 5, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xB6),
                         (2, 3, 5, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xB7),
                         (1, 2, 3, 5, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xB8),
                         (4, 5, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xB9),
                         (1, 4, 5, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xBA),
                         (2, 4, 5, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xBB),
                         (1, 2, 4, 5, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xBC),
                         (3, 4, 5, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xBD),
                         (1, 3, 4, 5, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xBE),
                         (2, 3, 4, 5, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xBF),
                         (1, 2, 3, 4, 5, 6, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xC0),
                         (7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xC1),
                         (1, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xC2),
                         (2, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xC3),
                         (1, 2, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xC4),
                         (3, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xC5),
                         (1, 3, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xC6),
                         (2, 3, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xC7),
                         (1, 2, 3, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xC8),
                         (4, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xC9),
                         (1, 4, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xCA),
                         (2, 4, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xCB),
                         (1, 2, 4, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xCC),
                         (3, 4, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xCD),
                         (1, 3, 4, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xCE),
                         (2, 3, 4, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xCF),
                         (1, 2, 3, 4, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xD0),
                         (5, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xD1),
                         (1, 5, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xD2),
                         (2, 5, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xD3),
                         (1, 2, 5, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xD4),
                         (3, 5, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xD5),
                         (1, 3, 5, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xD6),
                         (2, 3, 5, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xD7),
                         (1, 2, 3, 5, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xD8),
                         (4, 5, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xD9),
                         (1, 4, 5, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xDA),
                         (2, 4, 5, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xDB),
                         (1, 2, 4, 5, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xDC),
                         (3, 4, 5, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xDD),
                         (1, 3, 4, 5, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xDE),
                         (2, 3, 4, 5, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xDF),
                         (1, 2, 3, 4, 5, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xE0),
                         (6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xE1),
                         (1, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xE2),
                         (2, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xE3),
                         (1, 2, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xE4),
                         (3, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xE5),
                         (1, 3, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xE6),
                         (2, 3, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xE7),
                         (1, 2, 3, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xE8),
                         (4, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xE9),
                         (1, 4, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xEA),
                         (2, 4, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xEB),
                         (1, 2, 4, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xEC),
                         (3, 4, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xED),
                         (1, 3, 4, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xEE),
                         (2, 3, 4, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xEF),
                         (1, 2, 3, 4, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xF0),
                         (5, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xF1),
                         (1, 5, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xF2),
                         (2, 5, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xF3),
                         (1, 2, 5, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xF4),
                         (3, 5, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xF5),
                         (1, 3, 5, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xF6),
                         (2, 3, 5, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xF7),
                         (1, 2, 3, 5, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xF8),
                         (4, 5, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xF9),
                         (1, 4, 5, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xFA),
                         (2, 4, 5, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xFB),
                         (1, 2, 4, 5, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xFC),
                         (3, 4, 5, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xFD),
                         (1, 3, 4, 5, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xFE),
                         (2, 3, 4, 5, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0xFF),
                         (1, 2, 3, 4, 5, 6, 7, 8))
        self.assertEqual(self.cover_device._get_channels_from_response(0x100),
                         (9,))

    def test_answer_on_check(self):
        """Testing the _answer_on_check method."""
        self.assertEqual(self.cover_device._answer_on_check(
            b'\xAA\x04\x6B\x00\x6F\x98'),
            (1, 2, 3, 4, 6, 7))
        self.assertEqual(self.cover_device._answer_on_check(
            b'\xAA\x04\x6B\x00\x7F\x98'),
            (1, 2, 3, 4, 5, 6, 7))

    def test_answer_on_send(self):
        """Testing the _answer_on_send method."""
        # No information
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\x00\xb7'),
            elero_component.INFO_NO_INFORMATION)
        # Top position stop
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\x01\xb7'),
            elero_component.INFO_TOP_POSITION_STOP)
        # Bottom position stop
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\x02\xb7'),
            elero_component.INFO_BOTTOM_POSITION_STOP)
        # Intermediate position stop
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\x03\xb7'),
            elero_component.INFO_INTERMEDIATE_POSITION_STOP)
        # Tilt/ventilation position stop
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\x04\xb7'),
            elero_component.INFO_TILT_VENTILATION_POSITION_STOP)
        # Blocking
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\x05\xb7'),
            elero_component.INFO_BLOCKING)
        # Overheated
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\x06\xb7'),
            elero_component.INFO_OVERHEATED)
        # Timeout
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\x07\xb7'),
            elero_component.INFO_TIMEOUT)
        # Start to move up
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\x08\xb7'),
            elero_component.INFO_START_TO_MOVE_UP)
        # Start to move down
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\x09\xb7'),
            elero_component.INFO_START_TO_MOVE_DOWN)
        # Moving up
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\x0A\xb7'),
            elero_component.INFO_MOVING_UP)
        # Moving down
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\x0B\xb7'),
            elero_component.INFO_MOVING_DOWN)
        # Stopped in undefined position
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\x0D\xb7'),
            elero_component.INFO_STOPPED_IN_UNDEFINED_POSITION)
        # Top position stop wich is tilt position
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\x0E\xb7'),
            elero_component.INFO_TOP_POSITION_STOP_WICH_IS_TILT_POSITION)
        # Bottom position stop wich is intermediate position
        self.assertEqual(
            self.cover_device._answer_on_send(b'\xAA\x05\x4D\x00\x40\x0F\xb7'),
            elero_component.INFO_BOTTOM_POSITION_STOP_WICH_IS_INTERMEDIATE_POSITION)
        # Switching device switched off
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\x10\xb7'),
            elero_component.INFO_SWITCHING_DEVICE_SWITCHED_OFF)
        # Switching device switched on
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\x11\xb7'),
            elero_component.INFO_SWITCHING_DEVICE_SWITCHED_ON)
        # not exists
        self.assertEqual(self.cover_device._answer_on_send(
            b'\xAA\x05\x4D\x00\x40\xAC\xb7'),
            elero_component.INFO_UNKNOWN)
        # any others invalid
        for i in range(0x12, 0x100):
            self.assertEqual(self.cover_device._answer_on_send(
                b''.join([b'\xAA\x05\x4D\x00\x40',
                          bytes.fromhex(format(i, 'X')),
                          b'\xb7'])),
                elero_component.INFO_UNKNOWN)

    def test_answer_on_info(self):
        """Testing the _answer_on_info method."""
        self.test_answer_on_send()


if __name__ == '__main__':
    unittest.main()
