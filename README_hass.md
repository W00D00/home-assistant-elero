---
layout: page
title: "Elero Cover"
description: "Instructions on how to integrate Elero covers into Home Assistant."
date: 2018-07-05 10:00
sidebar: true
comments: false
sharing: true
footer: true
logo: elero.png
ha_category: Cover
ha_release: 0.7x
---


The `elero` cover platform allows you to control [Elero](https://www.elero.com) devices (such as venetian blinds, a rollershutters, tubular motors, electrical devices, rolling door drives).


## {% linkable_title Prerequisite %}

The ELero Transmitter Stick is a 15-channel handheld radio transmitter for bidirectional communication between transmitter and receiver(s). To use the receiver control of the Home Assistant, at least one receiver must be taught-in into the Elero Transmitter Stick. For further details of the learning procedure please visit the [Elero's Downloads webpage](https://www.elero.com/en/downloads-service/downloads/) and find the [Centero Operation instruction](https://www.elero.com/en/downloads-service/downloads/?tx_avelero_downloads%5Bdownload%5D=319&tx_avelero_downloads%5Baction%5D=download&cHash=5cf4212966ff0d58470d8cc9aa029066)


## {% linkable_title Configuration %}
To configure Elero Transmitter stick in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
elero:
```

{% configuration %}
  port:
    description: Name of the serial port to the Elero Transmitter Stick.
    required: false
    type: string
    default: "/dev/ttyUSB0"
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


{% Example configuration: %}

```yaml
# Example configuration.yaml entry
elero:
  port: '/dev/ttyUSB0'
  baudrate: 38400
```


To enable Elero Covers in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
cover:
  - platform: elero
    covers:<name of your cover or place or room>:
      name: <name of your cover device>
      channel: <channel number of your cover device>
      device_class: <type of your cover device>
```


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
        channel: 1
        device_class: window # roller shutter
      guestroom:
        name: Guest room
        channel: 2
        device_class: window # roller shutter
      childrenroom:
        name: George
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
Just copy the "custom_components" folder into your hassio "../config/custom_components/" folder.
Configurate your "/config/configuration.yaml" file and its "covers" and "groups" parts.
You ca find my developer example version.


<p class='note'>
**Known limitation:** This is a beat version. At now it is not possible to tilt the blinds.
</p>
