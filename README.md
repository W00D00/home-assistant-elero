
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

1. According to the [documentation of the Elero USB Transmitter](https://www.elero.com/en/downloads-service/downloads/?tx_avelero_downloads%5Baction%5D=search&tx_avelero_downloads%5Blanguage%5D=0&tx_avelero_downloads%5Bquery%5D=stick&tx_avelero_downloads%5Barchive%5D=&cHash=dd3c489f199ddf8e24e38a1d897d2812), more Elero devices could be controlled at the same time with one command. However, It does not work. This causes many timing and control problems. I tried to contact with Elero via mail however the company has so far given no answer to my question about this error.


# Elero features

The Elero Transmitter stick supports the following Elero device features:
- up
- down
- stop
- intermediate position
- ventilation / turning position

---

# Configuration of Elero platform
As many transmitters can be used as many needed.
You could use as many transmitters as you want. So, you can control more than 15 devices. The connected transmitter stickes are discoveried by automaticly, so by default you do not need to configure them.
In some special cases, you can configure every Elero USB Transmitter stick in your installation, add and setup the following settings to your `configuration.yaml` file to every stick:

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


The connected Elero transmitters are automatically recognized and configured by HA automatically.
The serial numbers of the connected transmitters can be found in the HA log and are needed for the further configuration. 
Make sure you have the logger set to the INFO level to see the log message. You can do this by adding following to the config file `configuration.yaml`:

```yaml
logger:
  default: info
```
Then you should see the following long line after a restart of HA:

```
Elero - an Elero Transmitter Stick is found on port: '<serial port>' with serial number: '<serial number>'.
```

Make sure to disable the logger config again afterwards to avoid excessive logging!

The given serial number of a transmitter should be used to match a HA channel to the transmitter in the yaml config file.


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
        - up (Elero UP)
        - down (Elero DOWN)
        - stop (Elero STOP)
        - set_position (0=DOWN, 25=VENT, 50=MOVING/UNDEF, 75=INT, 100=UP)
        - open_tilt (Elero INTERMEDIATE)
        - close_tilt (Elero VENTILATION)
        - stop_tilt (Elero STOP)
        - set_tilt_position (unsupported)

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

## Cover 'Position' and 'Tilt position' Sliders

Unfortunately, by default, the Position slider is not configurable on a cover so, the 'step' of the slider either. Thus, the `set_position` and the `set_tilt_position` functions are not usable. Another problem that the Elero devices are not supporting these functions.

For the Elero 'intermediate' function use the `open_tilt` HA function and the Elero 'ventilation' function use the `close_tilt` HA function.

Nevertheless, these controls are shown and useable only if the pop-up window of the given cover is open.

Alternative methods for the Elero 'intermediate' and the 'ventilation' functions:

1. [Call a Service](https://www.home-assistant.io/docs/scripts/service-calls/)

```yaml
entities:
  - name: Intermediate
    service: cover.close_cover_tilt
    service_data:
      entity_id: cover.all_cover_group
    type: call-service
  - name: Ventilation
    service: cover.open_cover_tilt
    service_data:
      entity_id: cover.all_cover_group
    type: call-service
```


2. An [`input_number`](https://www.home-assistant.io/integrations/input_number/) slider with automation.

```yaml
input_number:
    diningroom_set_position:
        name: Position
        mode: slider
        initial: 0
        min: 0
        max: 100
        step: 25

automation:
  - alias: diningroom_set_position
    trigger:
        platform: numeric_state
        entity_id: input_number.diningroom_set_position
        to: 25
    action:
        - service: cover.close_cover_tilt
          entity_id:
            - cover.diningroom

```

3. An [`input_select`](https://www.home-assistant.io/integrations/input_select/) Scene with automation.

```yaml
input_select:
    scene_diningroom:
        name: Scene
        options:
            - open
            - close
            - stop
            - intermediate
            - ventilation

automation:
  - alias: Diningroom scene
    trigger:
      platform: state
      entity_id: input_select.scene_diningroom
      to: intermediate
    action:
        - service: cover.close_cover_tilt
          entity_id:
            - cover.diningroom
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
## Manual Installation
Just copy the contents of the `custom_components` folder into the Home Assistant `../config/custom_components/` folder.

Configurate the `/config/configuration.yaml` file and its all linked files like `covers` and `groups`, etc. Restart the Home Assistant.

## HACS Installation
You can use [HACS](https://hacs.xyz) to install the custom component. You need to add this repository https://github.com/W00D00/home-assistant-elero as a custom repository in HACS.

## Example config files
Some example files can be found in the `config` folder as a help or starting point.

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
* 3.3.1 - March 11, 2023 [Fix Deprecated Constant Usage](https://github.com/W00D00/home-assistant-elero/pull/45)
* 3.3 - May 12, 2023 [Using remote transmitter with ser2net](https://github.com/W00D00/home-assistant-elero/pull/40) & [Fix execution on HA2023.5.](https://github.com/W00D00/home-assistant-elero/pull/43)
* 3.2.2 - November 17, 2022 [Introduce the unique ID](https://github.com/W00D00/home-assistant-elero/pull/38)
* 3.2.1 - March 10, 2022 [Fix TypeError on HA Shutdowm](https://github.com/W00D00/home-assistant-elero/pull/36)
* 3.2.0 - March 10, 2022 [Added support for HACS](https://github.com/W00D00/home-assistant-elero/issues/23)
* 3.1.0 - March 5, 2022 [Update dependencies for pip 20.3](https://github.com/W00D00/home-assistant-elero/issues/29)
* 3.0.0 - April 23, 2021 [Update manifest.json with version.](https://github.com/W00D00/home-assistant-elero/commit/d6bce117bc26c9b4cf54b649060e8ea3a8538816)
* 3.0 - Jan 19, 2020 [Appling required HA style guideline.](https://github.com/W00D00/home-assistant-elero/commit/e50debc234091f9b16261e9f20e9d90c9604f308)
* 2.92 - Jan 05, 2020 - [Refactor the serial write/read processes to solve the group problem. Versioning.](https://github.com/W00D00/home-assistant-elero/issues/11)
* 2.91 - Jan 02, 2020 - [Serial write/read improvement.](https://github.com/W00D00/home-assistant-elero/issues/11)
* 2.9 - Dec 30, 2019 - [Serial write/read improvement.](https://github.com/W00D00/home-assistant-elero/issues/11)
* 2.8 - Dec 24, 2019 - [Define serial read and write time outs. Extend the HA states with Elero states.](https://github.com/W00D00/home-assistant-elero/issues/11)
* 2.7 - Dec 13, 2019 - [The intermediate and ventilation commands and the statuses do not match to each other.](https://github.com/W00D00/home-assistant-elero/issues/10)
* 2.6 - Dec 8, 2019 - [The ventilation/intermediate functions are mixed up correction. New position slider with all Elero commands](https://github.com/W00D00/home-assistant-elero/issues/10)
* 2.5 - Dec 5, 2019 - [Response and cover position slider handling.](https://github.com/W00D00/home-assistant-elero/issues/8)
* 2.4 - Nov 16, 2019 - 'Position' slider is usable, [Response handling improvement](https://github.com/W00D00/home-assistant-elero/issues/8)
* 2.3 - Jul 15, 2019 - `no response` handling correction
* 2.2 - Jun 27, 2019 - New `no response` handling
* 2.1 - Jun 26, 2019 - [Store the Elero channels into the transmitter object](https://github.com/W00D00/home-assistant-elero/issues/6)
* 2.0 - Jun 21, 2019 - [Discover USB devices automatically](https://github.com/W00D00/home-assistant-elero/issues/4)
* 1.6 - Mar 10, 2019 - Correction of the implementation of the intermediate, ventilation position Function
* 1.5 - Nov 25, 2018 - Upper (9-15) channel state handling correction
* 1.4 - Oct 20, 2018 - Implementation of the Ventilation/Tilt and Intermediate position
* 1.3 - Sep 28, 2018 - Different Elero device handling
* 1.2 - Jul 9, 2018 - New State system
* 1.1 - Jun 24, 2018 - Release for beta test
* 1.0 - Jun 16, 2018 - Initial release





# Remote connection

Connect the Elero component to an USB stick that is connected to a Raspberry PI

## Installation of ser2net on a Raspberry PI

```bash
sudo rpi-update

sudo apt-get install ser2net
```

ser2net version 4.3.3 will be installed and a YAML configuration will be used.


### Configuration of ser2net

Connect the Elero transmitter stick to the Raspberry PI

For finding the ID of Elero transmitter call

```bash
ls /dev/serial/by-id
``` 


Update the ser2net.yaml configuration
```
sudo nano /etc/ser2net.yaml
```

and add the following configuration to the file. Use the ID of your stick.

```yaml
connection: &con02
  accepter: tcp,20109
  enable: off
 #connector: serialdev,/dev/ttyUSB1,38400n81,local
  connector: serialdev,/dev/serial/by-id/usb-elero_GmbH_Transmitter_Stick_AU00JHUU-if00-port0,38400n81,local
  options:
    kickolduser: true
```


### Fix problems of starting ser2net service after reboot

The manually ser2net application has some problems after raspberry pi's reboot. The USB-sticks can't be hosted as TCP ports and
the `sudo service ser2net status` shows Invalid name/port.

This can be simply fixed by a manual restart of the service `sudo service ser2net restart`.


This manual restart can be automatically called using crontab.
Add the restart 30s after a reboot (Absolute paths must be set in the crontab)

```
sudo crontab -e
```
and add the following line to the file
```
@reboot /usr/bin/sleep 30 && /usr/sbin/service ser2net restart
```

### Helper tools
Helper command to show open ports: `ss -tulw`


Helper script `list_ports.py` to show information of the USB device

```python
from serial.tools import list_ports

if __name__ == "__main__":
  
  for cp in list_ports.comports():
    print(cp)
    print("Device:", cp.device)
    print("Serial Number:", cp.serial_number)
    print("Product:", cp.product)
    print("Manufacturer:", cp.manufacturer)
    print("----")
```




## Homeassistant configuration of remote transmitters

The following values must be set to configure the Elero component to use remote transmitters. The serial number, the IP address and the port must match with the values configured before.

```yaml
elero:
    remote_transmitters:
        - serial_number: AU00JHUU
          address: "192.168.10.29:20109"
```


