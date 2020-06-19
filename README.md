# Home Assistant Config

These are the config files for my personal [Home Assistant](https://home-assistant.io/), home automation setup.

My goals:

1. Ditch SmartThings due to instability, confusing UIs/setup procedures, not a lot of local network processing, and their lack of official support for all of my devices.
2. Make all of my various hardware and services able to interact with each other.
3. Require no (or extremely minimal) use of a software based user interface.

# Hardware I'm using

* Aeotec Minimote, Multisensor, and Z-Stick Gen 5
* Amazon Echo Dots
* Apple TV
* Arlo Pro cameras
* GE Z-Wave wall outlets and dimmer modules
* Google Chromecast Ultra
* Google Home, Home hub, and Home mini
* Intel NUC to run [Home Assistant](https://home-assistant.io/)
* Liftmaster MyQ Garage Door opener
* Lutron Caséta dimmers, switches, fans, pico, remotes, and lamp modules
* Monoprice Z-Wave PIR motion sensors
* Nest thermostat, protects, cameras
* NuHeat Signature floor heating thermostat
* Philips Hue bulbs, lightstrips, dimmers
* Ring Pro Doorbell and spotlight cameras
* Samsung KS8000 TV
* Sonos speakers

# Supplemental software I'm using

* [Docker](https://www.docker.com/) to run Home Assistant in a container
* [Life360](https://www.life360.com/) for mobile device tracking
* [Plex](https://www.plex.tv/) media server

# Installing with Docker

1. Install Docker (and docker-compose)
1. Clone out this repository
1. Run: `docker-compose up -d` in a shell

