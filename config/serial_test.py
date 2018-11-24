
import time

import serial

from custom_components import elero as elero_platform
from custom_components.cover import elero as elero_component

# port, baud, data, parity, stop
ser = serial.Serial("COM3", 38400, 8, 'N', 1)
# transmitter_id, ser, read_sleep, read_timeout, write_sleep
elero_stick = elero_platform.EleroTransmitter(1, ser, 0.05, 1, 0.1)
# hass, transmitter, name, channels, device_class,
# supported_features, tilt_mode, tilt_sleep tilt_sleep
elero_device = elero_component.EleroCover(None, elero_stick,
                                          'Étkező', 7, 'venetian blind',
                                          ('up', 'down', 'stop', 'tilt'),
                                          'stepper', 0.06)


def test_function(payload):
    """Test the given functionality."""
    int_list = [elero_platform.BYTE_HEADER, elero_platform.BYTE_LENGTH_5,
                elero_platform.COMMAND_SEND,
                elero_device._get_upper_channel_bits(),
                elero_device._get_lower_channel_bits(),
                payload]
    elero_device._send_command(int_list)


def print_response():
    for k, v in elero_device._response.items():
        print(k, v)


"""
0x00 - 0x0F Nothing
0x10        Stop
0x11 - 1F   Nothing

Ha nincs ventilation/tilt pos programozva:
0x20    UP
0x21    UP
0x24    open the tilt by a step
0x25    UP

0x40    DOWN
0x41    DOWN
0x44    close the tilt by a step
0x45    DOWN

Ha van ventilation/tilt pos programozva:
0x20    UP
0x21    UP
0x24    ventilation pos, after open the tilt by a step
0x25    UP

0x40    DOWN
0x41    DOWN
0x44    close the tilt by a step
0x45    DOWN


"""
func = 1

if func == 1:
    h = 0x10
    print(hex(h))
    test_function(h)
    elero_device.get_response(elero_platform.RESPONSE_LENGTH_SEND)
    print_response()
elif func == 2:
    for h in range(0xd0, 0x100):
        print(hex(h))
        # STOP
        if h == 0x10:
            print("skiped\r\n")
            continue
        # UP
        if h == 0x20:
            print("skiped\r\n")
            continue
        # UP ???
        if h == 0x21:
            print("skiped\r\n")
            continue
        # Tilt/Ventilation pos
        if h == 0x24:
            print("skiped\r\n")
            continue
        # UP ???
        if h == 0x25:
            print("skiped\r\n")
            continue
        # Combio-867 / -868 / -915 JA pulse time
        if h == 0x32:
            print("skiped\r\n")
            continue
        # DOWN
        if h == 0x40:
            print("skiped\r\n")
            continue
        # DOWN ???
        if h == 0x41:
            print("skiped\r\n")
            continue
        # Intermadiate pos
        if h == 0x44:
            print("skiped\r\n")
            continue
        # Down ???
        if h == 0x45:
            print("skiped\r\n")
            continue

        test_function(h)
        elero_device.get_response(elero_platform.RESPONSE_LENGTH_SEND)
        print_response()
        print("wait...\r\n")
        time.sleep(5)
elif func == 3:
    elero_device.check()
    elero_device.get_response(elero_platform.RESPONSE_LENGTH_CHECK)
    print_response()
elif func == 4:
    elero_device.open_cover()
    elero_device.get_response(elero_platform.RESPONSE_LENGTH_CHECK)
    print_response()
