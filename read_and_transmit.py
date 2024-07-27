###############################################################
#                      Author: William Fowler                 #
#                         Date: 7/9/24                        #
#                   Project: NCAR Weather Sensing             #
#   Purpose: this script runs on a RP2040-LoRa                #
#   microcontroller which is running circuitpython. It will   #
#   read sensor information from the ltr390, bme680, and      #
#   pmsa003i and then transmit the received data over LoRa    #
#   to another LoRa-enabled deivce with the same network      #
#   parameters.                                               #
###############################################################

import time
import board
import busio
import digitalio

# sensor modules; installed from PyPi
import adafruit_ltr390
import adafruit_bme680
from adafruit_pm25.i2c import PM25_I2C

from LoRaTX import LoRa # import LoRa module configured in LoRa.py

# initialize I2C connection
i2c = board.I2C() # uses GP1 for SCL, GP0 for SDA

# initialize sensors
ltr390 = adafruit_ltr390.LTR390(i2c)
print('Found UV sensor...')
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)
bme680.sea_level_pressure = 1013.25 # setting sea level pressure
print('Found BME sensor...')
pmsa003i = PM25_I2C(i2c, None)
print('Found Air Quality sensor...')

while True:
    # initialize list to track data
    data = []
    
    # read UV sensor data. If there is a failure, try reading everything again,
    # do not transmit over LoRa
    try:
        data.append(ltr390.uvs)
        data.append(ltr390.light)
    except RuntimeError:
        print("Could not read uv sensor")
        continue
    
    # read BME sensor data
    try:
        data.append(bme680.temperature)
        data.append(bme680.gas)
        data.append(bme680.relative_humidity)
        data.append(bme680.pressure)
        data.append(bme680.altitude)
    except RuntimeError:
        print("Could not read bme sensor")
        continue
    
    # read air quality sensor data
    try:
        aqdata = pmsa003i.read()
        '''
        pm1.0, pm2.5, and pm10.0 concentration units report the number of particles
        with lengths less than that many micrometers. Standard uses a standardized
        pressure equivalent to sea level whereas environmental depends on the
        pressure in the current environment
        '''
        data.append(aqdata["pm10 standard"]) # < 1.0 micrometer
        data.append(aqdata["pm25 standard"]) # < 2.5 micrometers
        data.append(aqdata["pm100 standard"]) # < 10.0 micrometers
        data.append(aqdata["pm10 env"])
        data.append(aqdata["pm25 env"])
        data.append(aqdata["pm100 env"])
        '''
        measured in particles greater than _____ micrometers per 0.1L of air
        '''
        data.append(aqdata["particles 03um"]) # > 0.3um / 0.1L air
        data.append(aqdata["particles 05um"]) # > 0.5um / 0.1L air
        data.append(aqdata["particles 10um"]) # > 1.0um / 0.1L air
        data.append(aqdata["particles 25um"]) # > 2.5um / 0.1L air
        data.append(aqdata["particles 50um"]) # > 5.0um / 0.1L air
        data.append(aqdata["particles 100um"]) # > 10.0um / 0.1L air      
    except RuntimeError:
        print("Could not read air quality sensor")
        continue
    
    message = ""
    for datum in data:
        message += str(datum).strip() + " "
    
    messageList = list(message) # get list of characters
    for i in range(len(messageList)):
        messageList[i] = ord(messageList[i]) # convert to unicode value

    # transmit the values one at a time
    LoRa.beginPacket()
    LoRa.write(messageList, len(messageList))
    LoRa.endPacket()

    print(f"Transmitted: {message.strip()}")
    LoRa.wait()

        # Print transmit time and data rate
    print("Transmit time: {0:0.2f} ms | Data rate: {1:0.2f} byte/s".format(LoRa.transmitTime(), LoRa.dataRate()))
    time.sleep(60)
