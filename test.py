import mqttHA
from time import time, sleep, localtime, strftime


mqttHA.initialize('192.168.30.8', 'UserMQTT', 'MQTT')
mqttHA.publishHADiscover()
sleep(5)
while True:
	mqttHA.publishHAStatus(22.0,50.0,True,95.0)
	sleep(300)
