#!/usr/bin/python
import time
import os
import RPi.GPIO as GPIO

binCapacity = "Empty"

# Setup GPIOs
GPIO.setmode(GPIO.BCM)

# Define the LED GPIO pin and configure it as an output
GPIO.setup(26,GPIO.OUT)

# Turn on the LED for two seconds
GPIO.output(26, GPIO.HIGH)
time.sleep(2)
GPIO.output(26, GPIO.LOW)

# function to read distance from sensor
def read_distance():

    # specify GPIO pins to use for the Ultrasonic sensor
    TRIG = 2 # GPIO02
    ECHO = 3 # GPIO03

    # set pin mode and initialize
    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)
   
    # send a very short (10 micro seconds) pulse to "TRIG" pin
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)

    # wait for "ECHO" pin becomes HIGH
    signaloff = time.time()
    while GPIO.input(ECHO) != GPIO.HIGH:
        signaloff = time.time()

    # wait for "ECHO" pin becomes LOW
    signalon = signaloff
    while time.time() < signaloff + 0.1: # timeout in 0.1 seconds
        if GPIO.input(ECHO) == GPIO.LOW:
            signalon = time.time()
            break

    # cleanup GPIO state
    # GPIO.cleanup()

    # calculate distance from time difference
    # sound(ultrasonic) travels 340 m / seconds
    # distance (cm) can be obtained by 340(m/s) x 100(m/cm) * time(s) / 2 
    time_passed = signalon - signaloff
    distance = 340 * 100 * time_passed / 2

    # cleanup GPIO state
    #GPIO.cleanup()

    # since the sensor cannot guage over 500 cm, 
    # distance over 500 is considered as a noise
    if distance <= 500:
	time.sleep(2)
        return distance
    else:
        time.sleep(2)
	return None

# if executed directly (not import as library)
if __name__ == '__main__':

    while True:
        start_time = time.time()
        distance = read_distance()
        if distance:
            print "distance: %.1f cm" % (distance)
            os.system("mosquitto_pub -h beam.soracom.io -t sorapi -m '%.1f'" % (distance))
            
    	if distance <= 20 and distance > 0:
       	 	if binCapacity == "Empty":
                	binCapacity = "Full"
                	print("Time to take out the garbage!")
                	os.system("mosquitto_pub -h beam.soracom.io -t sorapi_bin -m 'Full'")
                	GPIO.output(26, GPIO.HIGH)
        	else:
                	GPIO.output(26, GPIO.HIGH)
    	elif distance > 20:
        	if binCapacity == "Full":
                	binCapacity = "Empty"
                	GPIO.output(26, GPIO.LOW)
                	print("Thanks for emptying the garbage!")
                	os.system("mosquitto_pub -h beam.soracom.io -t sorapi_bin -m 'Empty'")
        	else:
                	GPIO.output(26, GPIO.LOW)
    	else:
        	GPIO.output(26, GPIO.LOW)

	# wait for next loop
        wait = start_time + 1 - time.time()
        if wait > 0:
            time.sleep(wait)
