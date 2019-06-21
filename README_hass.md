---
layout: page
title: "Elero Cover"
description: "Instructions on how to integrate Elero covers into Home Assistant."
date: 2019-06-21 10:00
sidebar: true
comments: false
sharing: true
footer: true
logo: elero.png
ha_category: Cover
ha_release: 0.9x
---


This `elero` platform allows you to control different [Elero](https://www.elero.com) components/devices (such as venetian blinds, a roller shutters, tubular motors, electrical devices, rolling door drives, etc.).


## {% linkable_title Prerequisite %}

The Elero Transmitter Stick is a 15-channel handheld radio transmitter for bidirectional communication between transmitter and receiver(s).

To use the receiver control of the Home Assistant, at least one receiver must be taught-in into the Elero Transmitter Stick. For further details of the learning procedure please visit the [Elero's Downloads webpage](https://www.elero.com/en/downloads-service/downloads/) and find the [Centero Operation instruction](https://www.elero.com/en/downloads-service/downloads/?tx_avelero_downloads%5Bdownload%5D=319&tx_avelero_downloads%5Baction%5D=download&cHash=5cf4212966ff0d58470d8cc9aa029066)


## {% linkable_title Elero features %}

The Elero Transmitter stick supports the following Elero device features:
- up
- down
- stop
- tilt
    - open (intermediate position)
    - close (ventilation / turning position)
    - stop


## {% linkable_title Configuration %}
You can use as many transmitters as you want. So, you can control more than 15 devices.
You can configure every Elero USB Transmitter stick in your installation, add and setup the following settings to your `configuration.yaml` file to every stick:

```yaml
# Example configuration.yaml entry
elero:
```

{% configuration %}
  serial_number:
    description: Serial number if the given Transmitter Stick.
    required: false
    type: string
    default: -
  baudrate:
    description: You configure BaudRate as bits per second.
    required: false
    type: integer
    default: 38400
  bytesize:
    description: Number of data bits.
    required: false
    type: integer
    default: 8
  parity:
    description:  Enable parity checking.
    required: false
    type: string
    default: "None"
  stopbits:
    description: Number of stop bits.
    required: false
    type: integer
    default: 1
{% endconfiguration %}


The connected Elero transmitters are automatically recognized and set. The serial number of the given stick should be used to match a channel to the stick by you in the config file. You can find the serial numbers the HA log.

You can configure the connected devices with the followings in the `configuration.yaml` file if it is needed:


{% Example configuration: %}

```yaml
# Example configuration.yaml entry
elero:
  serial_number: 00000000
  baudrate: 9600
```


## {% linkable_title Configuration of the Elero cover component %}

To enable an Elero component like a covers in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
cover:
  - platform: elero
    covers:
      <name of your cover or place or room>:
      name: <name of your cover device>
      channel: <channel number of your cover device>
      device_class: <type of your cover device>
      supported_features:
          - <feature>
```


{% configuration %}
serial_number:
    description: The ID (number) of the given Elero Transmitter Stick. /
    The given channel is at that Elero USB Transmitter Stick.
    required: true
    type: integer
    default: -
    value: your choose
name:
    description: Name of your cover device that is displayed on the UI.
    required: true
    type: string
    default: -
    value: your choose
channel:
    description: Channel number of the cover device which is learned on the Elero USB Stick.
    required: true
    type: integer
    default: -
    value: one number between 1-15
device class:
    description: The class of the cover device, changing the device state and icon that is displayed on the UI.
    required: true
    type: string
    default: -
    value:
        - venetian blind
        - roller shutter
        - awning
        - rolling door
supported features:
    description: Functionalities of your cover device.
    required: true
    type: string
    default: -
    value:
        - up
        - down
        - stop
        - set_position (unsupported yet)
        - open_tilt
        - close_tilt
        - stop_tilt
        - set_tilt_position (unsupported yet)
{% endconfiguration %}


To create `Cover Groups` in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
  - platform: group
    name: <name of your cover group>
    entities:
      - cover.<name of your cover device>
```


{% Example configuration: %}

```yaml
# Example configuration.yaml entry
cover:
  - platform: elero
    covers:
      bathroom_small:
        name: Shower
        serial_number: 00000000
        channel: 1
        device_class: window # roller shutter
      guestroom:
        name: Guest room
        serial_number: 00000000
        channel: 2
        device_class: window # roller shutter
      childrenroom:
        name: George
        serial_number: 00000000
        channel: 3
        device_class: window # venetian blind
      bathroom_big:
        name: Bathroom
        channel: 4
        device_class: window # venetian blind
  - platform: group
    name: Roller shutters
    entities:
      - cover.shower
      - cover.guest_room
  - platform: group
    name: Venetian blinds
    entities:
      - cover.george
      - cover.bathroom
```


## {% linkable_title Functionality %}

The supported features are `open`/`close`/`stop`.


## {% linkable_title Installation %}
Just copy the contents of the `custom_components` folder into your Home Assistant `../config/custom_components/` folder.

Configurate your `/config/configuration.yaml` file and its all linked files like `covers` and `groups`, etc. what you did and filled. Restart your Home Assistant server and enjoy.
