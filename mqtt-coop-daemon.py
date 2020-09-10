import paho.mqtt.client as mqtt
import Adafruit_DHT as dht
import json
from time import time, sleep, localtime, strftime

# Eclipse Paho callbacks - http://www.eclipse.org/paho/clients/python/docs/#callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('MQTT connection established')
    else:
        print('Connection error with result code {} - {}'.format(str(rc), mqtt.connack_string(rc)))
        #kill main thread
        os._exit(1)

def on_publish(client, userdata, mid):
    #print_line('Data successfully published.')
    pass

mqttHost = '192.168.30.8'
mqttUser = 'UserMQTT'
mqttPwd = 'MQTT'
base_topic = 'homeassistant'
sleep_period = 300
dhtPin = 11
potPin = 2
daemon_enabled = True

print('Connecting to MQTT broker ...')
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_publish = on_publish

mqtt_client.username_pw_set(mqttUser, mqttPwd)

try:
    mqtt_client.connect(mqttHost,1883,60)
except:
    print('MQTT connection error. Please check network and IOTPi')
    sys.exit(1)
else:
    mqtt_client.loop_start()
    sleep(1.0) # some slack to establish the connection
   
# Initialize DHT sensor
sensor_name = 'winter_coop'
sensor = dht.DHT22

# Discovery Announcement
topic_path = '{}/sensor/{}'.format(base_topic, sensor_name)
base_payload = {
    "state_topic": "{}/state".format(topic_path).lower()
}

# Temperature
payload = dict(base_payload.items())
payload['unit_of_measurement'] = '°C'
payload['value_template'] = "{{ value_json.temperature }}"
payload['name'] = "{} Temperature".format(sensor_name)
payload['device_class'] = 'temperature'
payload['unique_id']= "{}_t".format(sensor_name)
payload['expire_after'] = "{}".format(2*sleep_period)
deviceDetails = dict()
deviceDetails['identifiers'] = "{}".format(sensor_name)
deviceDetails['name'] = "{}".format(sensor_name)
deviceDetails['model'] = 'Raspberry Pi'
deviceDetails['manufacturer'] = 'DIY'
payload['device'] = deviceDetails
print('Publishing to MQTT topic "{}/{}_temperature/config"'.format(topic_path, sensor_name).lower)
mqtt_client.publish('{}/{}_temperature/config'.format(topic_path, sensor_name).lower(), json.dumps(payload), 1, True)
# Humidity
payload = dict(base_payload.items())
payload['unit_of_measurement'] = '%'
payload['value_template'] = "{{ value_json.humidity }}"
payload['name'] = "{} Humidity".format(sensor_name)
payload['device_class'] = 'humidity'
payload['unique_id']= "{}_h".format(sensor_name)
payload['expire_after'] = "{}".format(2*sleep_period)
deviceDetails = dict()
deviceDetails['identifiers'] = "{}".format(sensor_name)
deviceDetails['name'] = "{}".format(sensor_name)
deviceDetails['model'] = 'Raspberry Pi'
deviceDetails['manufacturer'] = 'DIY'
payload['device'] = deviceDetails
print('Publishing to MQTT topic "{}/{}_humidity/config"'.format(topic_path, sensor_name).lower())
mqtt_client.publish('{}/{}_humidity/config'.format(topic_path, sensor_name).lower(), json.dumps(payload), 1, True)
# Door Percent
payload = dict(base_payload.items())
payload['unit_of_measurement'] = '%'
payload['value_template'] = "{{ value_json.door_percent }}"
payload['name'] = "{} Door Percent".format(sensor_name)
payload['unique_id']= "{}_dp".format(sensor_name)
payload['expire_after'] = "{}".format(2*sleep_period)
deviceDetails = dict()
deviceDetails['identifiers'] = "{}".format(sensor_name)
deviceDetails['name'] = "{}".format(sensor_name)
deviceDetails['model'] = 'Raspberry Pi'
deviceDetails['manufacturer'] = 'DIY'
payload['device'] = deviceDetails
print('Publishing to MQTT topic "{}/{}_door_percent/config"'.format(topic_path, sensor_name).lower())
mqtt_client.publish('{}/{}_door_percent/config'.format(topic_path, sensor_name).lower(), json.dumps(payload), 1, True)
#Binary Sensors
topic_path = '{}/binary_sensor/{}'.format(base_topic, sensor_name)
base_payload = {
    "state_topic": "{}/state".format(topic_path).lower()
}
# Door Open
payload = dict(base_payload.items())
payload['device_class'] = 'door'
payload['value_template'] = "{{ value_json.door_open }}"
payload['name'] = "{} Door Open".format(sensor_name)
payload['unique_id']= "{}_do".format(sensor_name)
payload['expire_after'] = "{}".format(2*sleep_period)
deviceDetails = dict()
deviceDetails['identifiers'] = "{}".format(sensor_name)
deviceDetails['name'] = "{}".format(sensor_name)
deviceDetails['model'] = 'Raspberry Pi'
deviceDetails['manufacturer'] = 'DIY'
payload['device'] = deviceDetails
print('Publishing to MQTT topic "{}/{}_door_open/config"'.format(topic_path, sensor_name).lower())
mqtt_client.publish('{}/{}_door_open/config'.format(topic_path, sensor_name).lower(), json.dumps(payload), 1, True)
# Heater On
payload = dict(base_payload.items())
payload['value_template'] = "{{ value_json.heater_on }}"
payload['name'] = "{} Heater On".format(sensor_name)
payload['unique_id']= "{}_heater".format(sensor_name)
payload['expire_after'] = "{}".format(2*sleep_period)
deviceDetails = dict()
deviceDetails['identifiers'] = "{}".format(sensor_name)
deviceDetails['name'] = "{}".format(sensor_name)
deviceDetails['model'] = 'Raspberry Pi'
deviceDetails['manufacturer'] = 'DIY'
payload['device'] = deviceDetails
print('Publishing to MQTT topic "{}/{}_heater_on/config"'.format(topic_path, sensor_name).lower())
mqtt_client.publish('{}/{}_heater_on/config'.format(topic_path, sensor_name).lower(), json.dumps(payload), 1, True)


# Sensor data retrieval and publication
while True:
    print('Retrieving data from DHT sensor...')
    #humidity, temperature = dht.read_retry(sensor, dhtPin)
    humidity = 50.0
    temperature = 20.0
    door_percent = 80.0
    heater_on = False
    if humidity is None and temperature is None:
        print('Unable to get data form sensor.')
        print()
        continue
    else:
        data = dict()
        data['humidity'] = '{0:0.1f}'.format(humidity)
        data['temperature'] = '{0:0.1f}'.format(temperature)
        data['door_percent'] = '{0:0.1f}'.format(door_percent)
        print('Result: {}'.format(json.dumps(data)))
        print('Publishing to MQTT topic "{}/sensor/{}/state"'.format(base_topic, sensor_name).lower())
        mqtt_client.publish('{}/sensor/{}/state'.format(base_topic, sensor_name).lower(), json.dumps(data))
        sleep(0.5) # some slack for the publish roundtrip and callback function
        #binary sensors now
        data = dict()
        if door_percent >= 90.0:
            data['door_open'] = 'On'
        else:
            data['door_open'] = 'Off'
        if heater_on == True:
            data['heater_on'] = 'On'
        else:
            data['heater_on'] = 'Off'
        print('Publishing to MQTT topic "{}/binary_sensor/{}/state"'.format(base_topic, sensor_name).lower())
        mqtt_client.publish('{}/binary_sensor/{}/state'.format(base_topic, sensor_name).lower(), json.dumps(data))		
        print('Status messages published')

    if daemon_enabled:
        print('Sleeping ({} seconds) ...'.format(sleep_period))
        sleep(sleep_period)
        print()
    else:
        print('Execution finished in non-daemon-mode')
        break




