import pigpio
import Adafruit_ADS1x15
import time

class PotSensorError(Exception):
    pass

#safe open = 1935
#danger open = 2035
#safe closed = 769
#danger closed = 518

doorIsOpening = False
doorIsClosing = False

gPotPin = None
gAdc = None
gGain = None
gSafeMaxVoltage = None
gSafeMinVoltage = None
gDangerMaxVoltage = None
gDangerMinVoltage = None
gPotOpenDirection = None
gPotClosedDirection = None

gMotorPin = None
gSpeed = None
gMaxTime = None
gMotorOpenDirection = None
gMotorClosedDirection = None
gPi = None

def setupMotorControl( gpioMotorPin, speed, maxTime, openDirection  ) :
	global gMotorPin
	global gSpeed
	global gMaxTime
	global gMotorOpenDirection
	global gMotorClosedDirection
	global gPi
	
	gMotorPin = gpioMotorPin
	gPi=pigpio.pi()
	gMotorOpenDirection = openDirection
	gMotorClosedDirection = -1 * openDirection
	gMaxTime = maxTime
	gSpeed = speed
	
def setupDoorSensor( adcPotPin, openDirection, safeMaxVoltage, safeMinVoltage, dangerMaxVoltage, dangerMinVoltage ) :
	global gPotPin
	global gAdc
	global gGain
	global gSafeMaxVoltage
	global gSafeMinVoltage
	global gDangerMaxVoltage
	global gDangerMinVoltage
	global gPotOpenDirection
	global gPotClosedDirection
	
	gPotPin = adcPotPin
	gGain = 1
	gAdc = Adafruit_ADS1x15.ADS1015()
	gDangerMaxVoltage = float(dangerMaxVoltage)
	gDangerMinVoltage = float(dangerMinVoltage)
	gSafeMinVoltage = float(safeMinVoltage)
	gSafeMaxVoltage = float(safeMaxVoltage)
	gPotOpenDirection = float(openDirection)
	gPotClosedDirection = float(-1 * openDirection)
	
def openDoor() :
	if gPi == None or gAdc == None :
		raise Exception("Call setupDoorSensor and/or setupMotorControl first")
	
	if isDoorOpen() :
		print('Door is already open!')
		return True

	startTime = time.time()
	currentTime = startTime
	runningTime = currentTime - startTime
		
	gPi.set_PWM_frequency(gMotorPin, 50)
	gPi.set_servo_pulsewidth(gMotorPin, motorSpeedToDutyCycle( gSpeed * gMotorOpenDirection ) )
		
	global doorIsOpening
	doorIsOpening = True

	while not isDoorOpen() and runningTime < gMaxTime :
		currentTime = time.time()
		runningTime = currentTime - startTime
		time.sleep(0.005)

	gPi.set_servo_pulsewidth(gMotorPin, 0 )
	gPi.set_PWM_frequency(gMotorPin, 0)
	time.sleep(0.5)
	doorIsOpening = False;
	
	retVal = False
	if isDoorOpen(20) :
		print('Door is now open')
		retVal = True
	else :
		print('Motor timeout: Door at {}'.format(getDoorOpenPercentage()))
		retVal = False

	return retVal
	
def closeDoor() :
	if gAdc == None or gPi == None :
		raise Exception("Call setupDoorSensor and/or setupMotorControl first")
	
	if isDoorClosed() :
		print('Door is already closed!')
		return True

	startTime = time.time()
	currentTime = startTime
	runningTime = currentTime - startTime
	
	gPi.set_PWM_frequency(gMotorPin, 50)
	gPi.set_servo_pulsewidth(gMotorPin, motorSpeedToDutyCycle( gSpeed * -1 * gMotorOpenDirection ) )

	global doorIsClosing
	doorIsClosing = True

	while not isDoorClosed() and runningTime < gMaxTime :
		currentTime = time.time()
		runningTime = currentTime - startTime
		time.sleep(0.005)

	gPi.set_servo_pulsewidth(gMotorPin, 0 )
	gPi.set_PWM_frequency(gMotorPin, 0)	
	time.sleep(0.5)
	doorIsClosing = False;

	retVal = False
	if isDoorClosed(10) :
		print('Door is now closed')
		retVal = True
	else :
		print('Motor timeout: Door at {}'.format(getDoorOpenPercentage()))
		retVal = False

	return retVal

def isDoorOpen( errorBar = 0 ) :
	if gAdc == None :
		raise Exception("Call setupDoorSensor first")

	percent = getDoorOpenPercentage()
			
	return percent + errorBar >= 100.0
	
def isDoorClosed( errorBar = 0 ) :
	if gAdc == None :
		raise Exception("Call setupDoorSensor first")
		
	percent = getDoorOpenPercentage()
	global doorIsClosing
			
	return percent - errorBar <= 0.0

def getPotReading() :
	if gAdc == None :
		raise Exception("Call setupDoorSensor first")
		
	global doorIsOpening
	global doorIsClosing
	sensorValue = gAdc.read_adc(gPotPin)
	
	if sensorValue == 2047 :
		raise PotSensorError("Pot reads 2047, probably unplugged")
	
	if doorIsOpening :
		return sensorValue + 175 * gPotOpenDirection
	elif doorIsClosing :
		return sensorValue + 200 * -1 * gPotOpenDirection
	else :
		return sensorValue
	
def getDoorOpenPercentage( useDanger = False ) :
	if gAdc == None :
		raise Exception("Call setupDoorSensor first")
	
	minVoltage = None
	maxVoltage = None
	if useDanger:
		minVoltage = gDangerMinVoltage
		maxVoltage = gDangerMaxVoltage
	else:
		minVoltage = gSafeMinVoltage
		maxVoltage = gSafeMaxVoltage
	
	voltage = float(getPotReading())
	percent = (voltage - minVoltage) / (maxVoltage - minVoltage)
	if gPotOpenDirection == -1 :
		percent = 1 - percent

	percent = percent * 100
	return percent

def motorSpeedToDutyCycle( motorSpeed ) :

	if motorSpeed > 0.0 :
		return 1800
	else :
		return 1250


	if gPi == None :
		raise Exception("Call setupMotorControl first")
		
	#Motor speed should be between -255 and 255
	#But we need to convert to a duty cycle for the servo/VEX motor controller 29
	#DutyCycle = PulseWidth/(1/frequency) = PulseWidth * frequency
	#frequency is 50hz
	#1.0, 1.5, and 2.0ms for rev, off, and fwd
	#-255 = 1.0ms and 255 = 2.0ms
	#510 = 1.0 ms.
	print(motorSpeed)
	pulseWidth = ((( motorSpeed + 255 ) / 510)  + 1 ) *0.001
	dutyCycle = pulseWidth * 50
	#duty cycle is calcuated as a decimal, but should be returned as a percent
	print(dutyCycle)
	return dutyCycle * 100
	
def  stopMotor() :
	if gPi == None :
		raise Exception("Call setupMotorControl first")

	gPi.set_servo_pulsewidth(gMotorPin, 0 )
	gPi.set_PWM_frequency(gMotorPin, 0)
