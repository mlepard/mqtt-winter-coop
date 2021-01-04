import paho.mqtt.client as mqtt
import json
from time import time, sleep, localtime, strftime
import doorControl
import temperatureControl



base_topic = 'homeassistant'
mqtt_client = None

last_temp = None
last_humidity = None
last_heater = None
last_door = None

# Eclipse Paho callbacks - http://www.eclipse.org/paho/clients/python/docs/#callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('MQTT connection established')
        client.subscribe('homeassistant/winter_coop/heater/set')
        print('MQTT subscribed to homeassistant/winter_coop/heater/set')
        client.subscribe('homeassistant/winter_coop/door/set')
        print('MQTT subscribed to homeassistant/winter_coop/door/set')
    else:
        print('Connection error with result code {} - {}'.format(str(rc), mqtt.connack_string(rc)))
        #kill main thread
        os._exit(1)

def on_publish(client, userdata, mid):
    #print_line('Data successfully published.')
    pass

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print('Data successfully subscribed.')
    pass

def on_log(client, userdata, level, buff):  # mqtt logs function
    print(buff)


def on_message(client, userdata, message):
    print('MQTT message on '+message.topic+" "+str(message.payload))
    if "heater" in message.topic:
        if "ON" in str(message.payload):
            temperatureControl.turnHeaterOn()
        elif "OFF" in str(message.payload):
            temperatureControl.turnHeaterOff()
        sleep(0.5)
        publishHAStatus(last_temp, last_humidity, temperatureControl.isHeaterOn(), last_door)
    elif "door" in message.topic:
        if "OPEN" in str(message.payload):
            doorControl.openDoor()
        elif "CLOSE" in str(message.payload):
            doorControl.closeDoor()
        publishHAStatus(last_temp, last_humidity, last_heater, doorControl.getDoorOpenPercentage())
    


def initialize(mqttHost, mqttUser, mqttPwd):
    global mqtt_client 
    mqtt_client = mqtt.Client()
#    mqtt_client.on_log = on_log
    mqtt_client.on_connect = on_connect
    mqtt_client.on_publish = on_publish
    mqtt_client.on_message = on_message
    mqtt_client.on_subscribe = on_subscribe
    mqtt_client.username_pw_set(mqttUser, mqttPwd)

    try:
        mqtt_client.connect(mqttHost,1883,60)
    except:
        print('MQTT connection error. Please check network and IOTPi')
        sys.exit(1)
    else:
        mqtt_client.loop_start()
        sleep(1.0) # some slack to establish the connection

def publishHADiscover():
    if mqtt_client == None:
        print('MQTT Not Initialized, call intitialize().')
        sys.exit(1)
    
    deviceDetails = dict()
    deviceDetails['identifiers'] = "winter_coop"
    deviceDetails['name'] = "Winter Coop"
    deviceDetails['model'] = 'Raspberry Pi'
    deviceDetails['manufacturer'] = 'DIY'

    #publish sensors discovery
    base_payload = {
        "state_topic": "homeassistant/winter_coop/state"
    }
    base_payload['device'] = deviceDetails

    payload = dict(base_payload.items())
    payload['expire_after'] = "{}".format(3*300)
    payload['unit_of_measurement'] = '°C'
    payload['value_template'] = "{{ value_json.temperature }}"
    payload['name'] = "Winter Coop Temperature"
    payload['device_class'] = 'temperature'
    payload['unique_id']= "winter_coop_temp"
    print('Publishing to MQTT topic "homeassistant/sensor/winter_coop/temperature/config"')
    mqtt_client.publish('homeassistant/sensor/winter_coop/temperature/config', json.dumps(payload), 1, True)

    payload = dict(base_payload.items())
    payload['expire_after'] = "{}".format(3*300)
    payload['unit_of_measurement'] = '%'
    payload['value_template'] = "{{ value_json.humidity }}"
    payload['name'] = "Winter Coop Humidity"
    payload['device_class'] = 'humidity'
    payload['unique_id']= "winter_coop_humidity"
    #print('Publishing to MQTT topic "homeassistant/sensor/winter_coop/humidity/config"')
    mqtt_client.publish('homeassistant/sensor/winter_coop/humidity/config', json.dumps(payload), 1, True)

    payload = dict(base_payload.items())
    payload['expire_after'] = "{}".format(3*300)
    payload['unit_of_measurement'] = '%'
    payload['value_template'] = "{{ value_json.door_percent }}"
    payload['name'] = "Winter Coop Door Percent"
    payload['unique_id']= "winter_coop_door_percent"
    #print('Publishing to MQTT topic "homeassistant/sensor/winter_coop/door_percent/config"')
    mqtt_client.publish('homeassistant/sensor/winter_coop/door_percent/config', json.dumps(payload), 1, True)


    #publish switch discovery
    payload = dict(base_payload.items())
    payload['value_template'] = "{{ value_json.heater }}"
    payload['name'] = "Winter Coop Heater"
    payload['command_topic'] = 'homeassistant/winter_coop/heater/set'
    payload['unique_id']= "winter_coop_heater"
    #print('Publishing to MQTT topic "homeassistant/switch/winter_coop/heater/config"')
    mqtt_client.publish('homeassistant/switch/winter_coop/heater/config', json.dumps(payload), 1, True)

    #publish door discovery
    payload = dict(base_payload.items())
    payload['value_template'] = "{{ value_json.door_status }}"
    payload['name'] = "Winter Coop Door"
    payload['command_topic'] = 'homeassistant/winter_coop/door/set'
    payload['unique_id']= "winter_coop_door"
    #print('Publishing to MQTT topic "homeassistant/cover/winter_coop/door/config"')
    mqtt_client.publish('homeassistant/cover/winter_coop/door/config', json.dumps(payload), 1, True)

def publishHAStatus( temperature, humidity, heater, door_percent ):
    global last_temp
    global last_humidity
    global last_heater
    global last_door

    data = dict()
    if humidity != None:
        data['humidity'] = '{0:.0f}'.format(humidity)
        last_humidity = humidity
    if temperature != None:    
        data['temperature'] = '{0:0.1f}'.format(temperature)
        last_temp = temperature
    if heater != None:
        if heater == True:
            data['heater'] = 'ON'
        else:
            data['heater'] = 'OFF'
        last_heater = heater
    if door_percent != None:
        if door_percent >= 85.0:
            data['door_status'] = 'open'
        elif door_percent <= 10.0:
            data['door_status'] = 'closed'
        data['door_percent'] = "{:.0f}".format(door_percent)
        last_door = door_percent
    #print('Result: {}'.format(json.dumps(data)))
    #print('Publishing to MQTT topic "homeassistant/winter_coop/state"')
    mqtt_client.publish('homeassistant/winter_coop/state', json.dumps(data))
    sleep(0.5) # some slack for the publish roundtrip and callback function
    #print('Status messages published')
