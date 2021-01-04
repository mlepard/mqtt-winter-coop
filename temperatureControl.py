import Adafruit_DHT
import RPi.GPIO as GPIO
import os

__DHT_PIN__  = None
__Heater_Pin__ = None
__DHT_TYPE__ = Adafruit_DHT.DHT22

def initTempControl(tempPin, heaterPin):
	global __DHT_PIN__ 
	global __DHT_TYPE__

	if __DHT_PIN__ is None: 
		__DHT_PIN__ = tempPin
	else:
		raise RuntimeError("Temperature Control already initialized...")
		return
	
	global __Heater_Pin__
	if __Heater_Pin__ is None:
		__Heater_Pin__ = heaterPin
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(__Heater_Pin__, GPIO.OUT)
	else:
		raise RuntimeError("Temperature Control already initialized...")
		return
		
def getTemperature() :
	global __DHT_PIN__ 
	global __DHT_TYPE__
	if __DHT_PIN__ is None:
		print("initTempControl not called...")
		return None
	#get the current temperature
	humidity, temp = Adafruit_DHT.read_retry(__DHT_TYPE__, __DHT_PIN__)
	if temp is None:
		print("Can't get temp, exiting...")		
	return temp		
		
def getTemperatureAndHumidity() :
	global __DHT_PIN__ 
	global __DHT_TYPE__
	if __DHT_PIN__ is None:
		print("initTempControl not called...")
		return None
	#get the current temperature
	humidity, temp = Adafruit_DHT.read_retry(__DHT_TYPE__, __DHT_PIN__)
	if temp is None:
		print("Can't get temp, exiting...")
	if humidity is None:
		print("Can't get humidity, exiting...")		
	return (temp, humidity)
	
def turnHeaterOn() :
	global __Heater_Pin__
	if __Heater_Pin__ is None:
		print("initTempControl not called...")
		return
	GPIO.output(__Heater_Pin__, 1)
	
def turnHeaterOff() :
	if __Heater_Pin__ is None:
		print("initTempControl not called...")
		return
	GPIO.output(__Heater_Pin__, 0)
	
def isHeaterOn() :
	global __Heater_Pin__
	if __Heater_Pin__ is None:
		print("initTempControl not called...")
		return
	return GPIO.input(__Heater_Pin__)
