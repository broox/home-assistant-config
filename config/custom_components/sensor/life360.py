"""
@ Author      : Suresh Kalavala
@ Date        : 05/24/2017
@ Description : Life360 Sensor - It queries Life360 API and retrieves
                data at a specified interval and dumpt into MQTT

@ Notes:        Copy this file and place it in your
                "Home Assistant Config folder\custom_components\sensor\" folder
                Copy corresponding Life360 Package frommy repo,
                and make sure you have MQTT installed and Configured
                Make sure the life360 password don't contain '#' or '$' symbols
"""

from datetime import timedelta
import logging
import json
import urllib
import requests

import voluptuous as vol
import homeassistant.components.mqtt as mqtt

from io import StringIO
from homeassistant.components.mqtt import (CONF_STATE_TOPIC, CONF_COMMAND_TOPIC, CONF_QOS, CONF_RETAIN)
from homeassistant.helpers import template
from homeassistant.exceptions import TemplateError
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME, CONF_VALUE_TEMPLATE, CONF_UNIT_OF_MEASUREMENT,
    STATE_UNKNOWN)
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['mqtt']

DEFAULT_NAME = 'Life360 Sensor'
CONST_MQTT_TOPIC = "mqtt_topic"
CONST_STATE_ERROR = "error"
CONST_STATE_RUNNING = "running"
CONST_USERNAME = "username"
CONST_PASSWORD = "password"


SCAN_INTERVAL = timedelta(seconds=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONST_USERNAME): cv.string,
    vol.Required(CONST_PASSWORD): cv.string,
    vol.Required(CONST_MQTT_TOPIC): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_UNIT_OF_MEASUREMENT): cv.string,
    vol.Optional(CONF_VALUE_TEMPLATE): cv.template,
})

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Life360 Sensor."""
    name = config.get(CONF_NAME)
    username = config.get(CONST_USERNAME)
    password = config.get(CONST_PASSWORD)
    mqtt_topic = config.get(CONST_MQTT_TOPIC)

    unit = config.get(CONF_UNIT_OF_MEASUREMENT)
    value_template = config.get(CONF_VALUE_TEMPLATE)
    if value_template is not None:
        value_template.hass = hass

    _LOGGER.info("Setting up life360")
    data = Life360SensorData(username, password, mqtt_topic, hass)

    add_devices([Life360Sensor(hass, data, name, unit, value_template)])


class Life360Sensor(Entity):
    """Representation of a sensor."""

    def __init__(self, hass, data, name, unit_of_measurement, value_template):
        """Initialize the sensor."""
        self._hass = hass
        self.data = data
        self._name = name
        self._state = STATE_UNKNOWN
        self._unit_of_measurement = unit_of_measurement
        self._value_template = value_template
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    def update(self):
        """Get the latest data and updates the state."""
        self.data.update()
        value = self.data.value

        if value is None:
            value = STATE_UNKNOWN
        elif self._value_template is not None:
            self._state = self._value_template.render_with_possible_json_value(
                value, STATE_UNKNOWN)
        else:
            self._state = value


class Life360SensorData(object):
    """The class for handling the data retrieval."""

    def __init__(self, username, password, mqtt_topic, hass):
        """Initialize the data object."""
        self.username = username
        self.password = password
        self.hass = hass
        self.value = None
        self.mqtt_topic = mqtt_topic
        self.mqtt_retain = True
        self.mqtt_qos = 0

    def update(self):

        try:
            """ Prepare and Execute Commands """
            authorization_token = "cFJFcXVnYWJSZXRyZTRFc3RldGhlcnVmcmVQdW1hbUV4dWNyRUh1YzptM2ZydXBSZXRSZXN3ZXJFQ2hBUHJFOTZxYWtFZHI0Vg=="

            api = life360_request(authorization_token=authorization_token, username=self.username, password=self.password)
            payload = None
            if api.authenticate():
                #Grab some circles returns json
                circles =  api.get_circles()
                        
                #grab id
                circle_id = circles[0]['id']
                                    
                #Let's get your circle!
                payload  = api.get_circle(circle_id)

            if payload != None:
                self.save_payload_to_mqtt ( self.mqtt_topic, json.dumps(payload ))
                data =  payload 
                for member in data["members"]:
                    topic = StringBuilder()
                    topic.Append("owntracks/")
                    topic.Append(member["firstName"].lower())
                    topic.Append("/")
                    topic.Append(member["firstName"].lower())
                    topic = topic

                    msgPayload = StringBuilder()
                    msgPayload.Append("{")
                    msgPayload.Append("\"t\":\"p\"")
                    msgPayload.Append(",")

                    msgPayload.Append("\"tst\":")
                    msgPayload.Append(member['location']['timestamp'])
                    msgPayload.Append(",")

                    msgPayload.Append("\"acc\":")
                    msgPayload.Append(member['location']['accuracy'])
                    msgPayload.Append(",")

                    msgPayload.Append("\"_type\":\"location\"")
                    msgPayload.Append(",")

                    msgPayload.Append("\"alt\":\"0\"")
                    msgPayload.Append(",")

                    msgPayload.Append("\"_cp\":\"false\"")
                    msgPayload.Append(",")

                    msgPayload.Append("\"lon\":")
                    msgPayload.Append(member['location']['longitude'])
                    msgPayload.Append(",")

                    msgPayload.Append("\"lat\":")
                    msgPayload.Append(member['location']['latitude'])
                    msgPayload.Append(",")

                    msgPayload.Append("\"batt\":")
                    msgPayload.Append(member['location']['battery'])
                    msgPayload.Append(",")

                    if str(member['location']['wifiState']) == "1":
                        msgPayload.Append("\"conn\":\"w\"")
                        msgPayload.Append(",")

                    msgPayload.Append("\"vel\":")
                    msgPayload.Append(str(member['location']['speed']))
                    msgPayload.Append(",")

                    msgPayload.Append("\"charging\":")
                    msgPayload.Append(member['location']['charge'])
                    msgPayload.Append("}")

                    self.save_payload_to_mqtt ( str(topic), str(msgPayload) )
                self.value = CONST_STATE_RUNNING
            else:
                self.value = CONST_STATE_ERROR

        except Exception as e:
            self.value = CONST_STATE_ERROR

    def save_payload_to_mqtt( self, topic, payload ):

        try:
            """mqtt.async_publish ( self.hass, topic, payload, self.mqtt_qos, self.mqtt_retain )"""
            _LOGGER.info("topic: %s", topic)
            _LOGGER.info("payload: %s", payload)
            mqtt.publish ( self.hass, topic, payload, self.mqtt_qos, self.mqtt_retain )

        except:
            _LOGGER.error( "Error saving Life360 data to mqtt." )

class StringBuilder:
     _file_str = None

     def __init__(self):
         self._file_str = StringIO()

     def Append(self, str):
         self._file_str.write(str)

     def __str__(self):
         return self._file_str.getvalue()

class life360_request:
    
    base_url = "https://api.life360.com/v3/"
    token_url = "oauth2/token.json"
    circles_url = "circles.json"
    circle_url = "circles/"

    def __init__(self, authorization_token=None, username=None, password=None):
        self.authorization_token = authorization_token
        self.username = username
        self.password = password

    def make_request(self, url, params=None, method='GET', authheader=None):
        headers = {'Accept': 'application/json'}
        if authheader:
            headers.update({'Authorization': authheader, 'cache-control': "no-cache",})
        
        if method == 'GET':
            r = requests.get(url, headers=headers)
        elif method == 'POST':
            r = requests.post(url, data=params, headers=headers)

        return r.json()

    def authenticate(self):
        

        url = self.base_url + self.token_url
        params = {
            "grant_type":"password",
            "username":self.username,
            "password":self.password,
        }

        r = self.make_request(url=url, params=params, method='POST', authheader="Basic " + self.authorization_token)
        try:
            self.access_token = r['access_token']
            return True
        except:
            return False

    def get_circles(self):
        url = self.base_url + self.circles_url
        authheader="bearer " + self.access_token
        r = self.make_request(url=url, method='GET', authheader=authheader)
        return r['circles']

    def get_circle(self, circle_id):
        url = self.base_url + self.circle_url + circle_id
        authheader="bearer " + self.access_token
        r = self.make_request(url=url, method='GET', authheader=authheader)
        return r

   