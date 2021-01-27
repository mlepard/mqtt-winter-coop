import mqttHA
import temperatureControl
import doorControl
import RPi.GPIO as GPIO 
import json
from time import time, sleep, localtime, strftime


heaterPin = 23
temperaturePin = 11
motorPin = 24
potPin = 2 

printDebug = True
daemon_enabled = True
sleep_period = 300

mqttHA.initialize('192.168.30.7', 'UserMQTT', 'MQTT')
mqttHA.publishHADiscover()
GPIO.setwarnings(False)
temperatureControl.initTempControl(temperaturePin,heaterPin)
doorControl.setupDoorSensor(potPin, 1, 1800, 700, 1950, 450)
doorControl.setupMotorControl(motorPin, 175, 5.0, 1)

# Sensor data retrieval and publication
while True:
    print('Retrieving data from DHT sensor...')
    temp, humidity = temperatureControl.getTemperatureAndHumidity()
    heater_on = temperatureControl.isHeaterOn()
    door_percent = doorControl.getDoorOpenPercentage()
#    print(doorControl.getPotReading())
    if humidity is None and temp is None:
        print('Unable to get data form sensor.')
        continue
    else:
        mqttHA.publishHAStatus(temp, humidity, heater_on, door_percent)

    if daemon_enabled:
        print('Sleeping ({} seconds) ...'.format(sleep_period))
        sleep(sleep_period)
        print()
    else:
        print('Execution finished in non-daemon-mode')
        break




