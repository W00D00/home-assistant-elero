
> ## 🛠 Status: In Development
> This lib is currently in development. I encourage you to use it and give me your feedback, but there are things that haven't been finalized yet and you can expect some changes.

![Elero Logo](elero.png) ![Home Assistant Logo](home_assistant_logo.png)

Elero Python lib to the Home Assistant home automation platform
===============================================================

[Home Assistant](https://www.home-assistant.io/) is a home automation platform running on Python 3. It is able to track and control all devices at home and offer a platform for automating control.

This `elero` platform allows you to control different [Elero](https://www.elero.com) components/devices (such as venetian blinds, a roller shutters, tubular motors, electrical devices, rolling door drives, etc.).

---

# Prerequisite

The Elero Transmitter Stick is a 15-channel handheld radio transmitter for bidirectional communication between transmitter and receiver(s).

To use the receiver control of the Home Assistant, at least one receiver must be taught-in into the Elero Transmitter Stick. For further details of the learning procedure please visit the [Elero's Downloads webpage](https://www.elero.com/en/downloads-service/downloads/) and find the [Centero Operation instruction](https://www.elero.com/en/downloads-service/downloads/?tx_avelero_downloads%5Bdownload%5D=319&tx_avelero_downloads%5Baction%5D=download&cHash=5cf4212966ff0d58470d8cc9aa029066)

# Limitations

1. According to the documentation of the Elero USB Transmitter I should control more covers with one command. However, It is not working for me yet. This causes many timing and control problems. I will try to solve it as soon as I know.
This is why you use the HA cover group.

# Elero features

The Elero Transmitter stick supports the following Elero device features:
- up*
- down*
- stop*
- tilt*
    - open*
    - close*
    - stop*
- intermediate position*
- ventilation / turning position*

*implemented

**not implemented or not functional fully/correctly

---

# Configuration of Elero platform
You can use as many transmitter as you want. So, you can control more than 15 devices.
You need to configure every Elero USB Transmitter sticks in your installation, add and setup the following settings to your `configuration.yaml` file to every stick:

- **transmitter_id:**
    - **description:** The ID (number) of the given Elero Transmitter Stick.
    - **required:** true
    - **type:** integer
    - **default:** -
- **port:**
    - **description:** Name of the serial port to the Elero Transmitter Stick.
    - **required:** false
    - **type:** string
    - **default:** "/dev/ttyUSB0"
- **baudrate:**
    - **description:** You configure BaudRate as bits per second.
    - **required:** false
    - **type:** integer
    - **default:** 38400
- **bytesize:**
    - **description:** Number of data bits.
    - **required:** false
    - **type:** integer
    - **default:** 8
- **parity:**
    - **description:**  Enable parity checking.
    - **required:** false
    - **type:** string
    - **default:** "N"
- **stopbits:**
    - **description:** Number of stop bits.
    - **required:** false
    - **type:** integer
    - **default:*** 1
- **read_sleep:**
    - **description:** The seconds of the sleeping loop of the serial read process.
    - **required:** false
    - **type:** integer
    - **default:** 0.01
- **read_timeout:**
    - **description:** The maximum seconds to wait for serial data.
    - **required:** false
    - **type:** integer
    - **default:** 2.0
- **write_sleep:**
    - **description:** The seconds of the wait loop to the serial data write out before new data is send.
    - **required:** false
    - **type:** float
    - **default:** 0.06

If you have only one device and it is plugged into the '/dev/ttyUSB0' USB port of your board you have to configure it with the following in the `configuration.yaml` file:

Example of the basic configuration:

```yaml
# Example configuration.yaml entry
elero:
    transmitters:
        - transmitter_id: 1
          port: '/dev/ttyUSB0'
```

Example of the full configuration:

```yaml
# Example configuration.yaml entry
elero:
    transmitters:
        - transmitter_id: 1
          port: '/dev/ttyUSB0'
          baudrate: 38400
          bytesize: 8
          parity: 'N'
          stopbits: 1
          read_sleep: 0.05
          read_timeout: 2.5
          write_sleep: 0.08
```

---

# Configuration of the Elero cover component

To enable an Elero component like a covers in your installation, add the following to your `configuration.yaml` file:

- **transmitter_id:**
    - **description:** The ID (number) of the given Elero Transmitter Stick. /
    The given channel is at that Elero USB Transmitter Stick.
    - **required:** true
    - **type:** integer
    - **default:** -
    - **value:** your choose
- **name:**
    - **description:** Name of your cover device that is displayed on the UI.
    - **required:** true
    - **type:** string
    - **default:** -
    - **value:** your choose
- **channel:**
    - **description:** Channel number of the cover device which is learned on the Elero USB Stick.
    - **required:** true
    - **type:** integer
    - **default:** -
    - **value:** one number between 1-15
- **device class:**
    - **description:** The class of the cover device, changing the device state and icon that is displayed on the UI.
    - **required:** true
    - **type:** string
    - **default:** -
    - **value:**
        - venetian blind
        - roller shutter
        - awning
        - rolling door
- **supported features:**
    - **description:** Functionalities of your cover device.
    - **required:** true
    - **type:** string
    - **default:** -
    - **value:**
        - up
        - down
        - stop
        - set_position
        - open_tilt
        - close_tilt
        - stop_tilt
        - set_tilt_position

Example of a simple cover setup:
```yaml
# Example configuration.yaml entry
cover:
    - platform: elero
      covers:
          bathroom_small:
              transmitter_id: 1
              name: Shower
              channel:
                  - 1
              device_class: roller shutter
              supported_features:
                  - up
                  - down
                  - stop
```

---

## Cover groups
To create `Cover Groups` in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
cover:
    - platform: group
      name: "All Cover"
      entities:
          - cover.shower
          - cover.george
```

---

# Installation of the lib
Just copy the contents of the `custom_components` folder into your Home Assistant `../config/custom_components/` folder.

Configurate your `/config/configuration.yaml` file and its all linked files like `covers` and `groups`, etc. what you did and filled. Restart your Home Assistant server and enjoy.

## Example config files
You can find my example files in the 'config' folder as a starting point for your Elero platform and component setup like a cover.

---------------

# Automation

It is possible to specify triggers for automation of your covers.

```yaml
# Example automations.yaml entry
# Covers
    - alias: 'Close the covers before sunset'
      trigger:
        platform: sun
        event: sunset
        offset: '+00:30:00'
      action:
        service: cover.close_cover
        entity_id: cover.all_Cover
```
---

# Waiting for implementation

- one command controls more covers


# Known issues:

- ...

---

**If you have any question or you faced with trouble, do not hesitate to contact me, all comments, insight, criticism is welcomed!**

---
