
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

1. According to the documentation of the Elero USB Transmitter, more Elero devices could be controlled at the same time with one command. However, It does not work. This causes many timing and control problems. I tried to contact with Elero via mail however the company has so far given no answer to my question about this error.


# Elero features

The Elero Transmitter stick supports the following Elero device features:
- up
- down
- stop
- tilt
    - open (intermediate position)
    - close (ventilation / turning position)
    - stop

---

# Configuration of Elero platform
As many transmitters can be used as many needed.
You could use as many transmitters as you want. So, you can control more than 15 devices.
You can configure every Elero USB Transmitter stick in your installation, add and setup the following settings to your `configuration.yaml` file to every stick:

- **serial_number:**
    - **description:** The serial number of the given Elero Transmitter Stick.
    - **required:** false
    - **type:** string
    - **default:** -
- **baudrate:**
    - **description:** Baud Rate as bits per second.
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


The connected Elero transmitters are automatically recognized and configured by HA.
The serial numbers of the connected transmitters can be found in the HA log to the further configuration.
The serial number of the given transmitter should be used to match a HA channel to the transmitter in the yaml config file.


The connected devices could be configured with the followings in the `configuration.yaml` file:

Example of the configuration:

```yaml
# Example configuration.yaml entry
elero:
    transmitters:
        - serial_number: 00000000
          baudrate: 38400
          bytesize: 8
          parity: 'N'
          stopbits: 1
```

---

# Configuration of the Elero cover component

To enable an Elero component like a covers in an installation, add the following to into the `configuration.yaml` file:

- **serial_number:**
    - **description:** The serial number of the given Elero Transmitter Stick.
    - **required:** true
    - **type:** integer
    - **default:** -
    - **value:** your choose
- **name:**
    - **description:** Name of the cover that is displayed on the UI.
    - **required:** true
    - **type:** string
    - **default:** -
    - **value:** your choose
- **channel:**
    - **description:** The learned channel number on the Elero USB Stick.
    - **required:** true
    - **type:** integer
    - **default:** -
    - **value:** one number between 1-15
- **device class:**
    - **description:** The class of the cover. It affects the device state and icon that is displayed on the UI.
    - **required:** true
    - **type:** string
    - **default:** -
    - **value:**
        - venetian blind
        - roller shutter
        - awning
        - rolling door
- **supported features:**
    - **description:** Functionalities of the cover.
    - **required:** true
    - **type:** string
    - **default:** -
    - **value:**
        - up
        - down
        - stop
        - set_position (unsupported yet)
        - open_tilt
        - close_tilt
        - stop_tilt
        - set_tilt_position (unsupported yet)

Example of a simple cover setup:
```yaml
# Example configuration.yaml entry
cover:
    - platform: elero
      covers:
          bathroom_small:
              serial_number: 00000000
              name: Shower
              channel: 1
              device_class: roller shutter
              supported_features:
                  - up
                  - down
                  - stop
```

---

## Cover groups
To create `Cover Groups` in an installation, add the following into the `configuration.yaml` file:

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
Just copy the contents of the `custom_components` folder into the Home Assistant `../config/custom_components/` folder.

Configurate the `/config/configuration.yaml` file and its all linked files like `covers` and `groups`, etc. Restart the Home Assistant.

## Example config files
Some example files can be found in the 'config' folder as a help or starting point.

---------------

# Automation

It is possible to specify triggers for automation of your covers.

```yaml
# Example automations.yaml entry
# Covers
    - alias: 'Close the covers after sunset'
      trigger:
        platform: sun
        event: sunset
        offset: '+00:30:00'
      action:
        service: cover.close_cover
        entity_id: cover.all_Cover
```
---

# Report an issue:

Please use the Github Issues section to report a problem or feature request: https://github.com/W00D00/home-assistant-elero/issues/new


# Known issues:

Please see the Issues section: https://github.com/W00D00/home-assistant-elero/issues

# Contribution:

Please, Test first!

For minor fixes and documentation, please go ahead and submit a pull request. A gentle introduction to the process can be found [here](https://www.freecodecamp.org/news/a-simple-git-guide-and-cheat-sheet-for-open-source-contributors/).

Check out the list of issues. Working on them is a great way to move the project forward.

Larger changes (rewriting parts of existing code from scratch, adding new functions) should generally be discussed by opening an issue first.

Feature branches with lots of small commits (especially titled "oops", "fix typo", "forgot to add file", etc.) should be squashed before opening a pull request. At the same time, please refrain from putting multiple unrelated changes into a single pull request.

---

**If you have any question or you have faced with trouble, do not hesitate to contact me, all comments, insight, criticism is welcomed!**

---

# Version
* 2.3 - Jul 15, 2019 - No response handling correction
* 2.2 - Jun 27, 2019 - New no response handling
* 2.1 - Jun 26, 2019 - Store the Elero channels into the transmitter object
* 2.0 - Jun 21, 2019 - Discover USB devices automatically
* 1.6 - Mar 10, 2019 - Intermediate, ventilation position
* 1.5 - Nov 25, 2018 - Upper (9-15) channel state handling correction
* 1.4 - Oct 20, 2018 - Ventilation/Tilt and Intermediate position
* 1.3 - Sep 28, 2018 - Different Elero device handling
* 1.2 - Jul 9, 2018 - New State system
* 1.1 - Jun 24, 2018 - Release for beta test
* 1.0 - Jun 16, 2018 - Initial release
