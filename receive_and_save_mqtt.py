import os
import sys
import time
from LoRaRX import LoRa  # import LoRa module configured in LoRa.py
from datetime import datetime
import pytz # need sudo pip install pytz

import paho.mqtt.client as mqtt

# define MQTT config
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'sensor_data'

# DCurrent timezone set to CST
tz = pytz.timezone('America/Chicago')

def parse_sensor_data(sensor_data_string):
    # Define the keys corresponding to the metrics
    keys = [
        'uv', 'ambient_light', 'temperature', 'gas', 'humidity', 'pressure', 'altitude',
        'pm10_std', 'pm25_std', 'pm100_std', 'pm10_env', 'pm25_env', 'pm100_env',
        'part_03', 'part_05', 'part_10', 'part_25', 'part_50', 'part_100', 'date', 'time'
    ]
    
    # Split the incoming string by spaces
    values = sensor_data_string.split() # all datatypes string
    
    # Create a dictionary by zipping keys and values together
    sensor_data_dict = dict(zip(keys, values))
    
    return sensor_data_dict

# publish data
def publish_data_to_mqtt(client, data):
    client.publish(MQTT_TOPIC, data)
    print(f" [x] Sent {data} to MQTT")

# start MQTT service
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

# index for messages
index = 0

while True:
    try:
        # Request for receiving new LoRa packet
        LoRa.request()
        # Wait for incoming LoRa packet
        LoRa.wait()

        # Put received packet to data variable
        data = ""
        while LoRa.available() > 0:
            data += chr(LoRa.read())

        # Write received data to the file only if it exists
        if data.strip():

            # write the current date and time
            utc_now = datetime.now(pytz.utc) # current UTC time
            curr_time = utc_now.astimezone(tz) # convert to CST
            data += curr_time.strftime('%Y-%m-%d %H:%M:%S')

            # parse data into dict
            parsed_data = parse_sensor_data(data)
            # print(parsed_data)

            # Get current epoch time
            epoch_time = int(time.time())
            epoch_str = str(epoch_time)

            # prepare message to publish
            message = ('sensor_data,'
                       'host=raspberrypi,'
                       f'index={index},'
                       f'epoch_time={epoch_time},'
                       f'uv={parsed_data["uv"]},'
                       f'ambient_light={parsed_data["ambient_light"]},'
                       f'humidity={parsed_data["humidity"]},'
                       f'pressure={parsed_data["pressure"]},'
                       f'altitude={parsed_data["altitude"]},'
                       f'pm10_std={parsed_data["pm10_std"]},'
                       f'pm25_std={parsed_data["pm25_std"]},'
                       f'pm100_std={parsed_data["pm100_std"]},'
                       f'pm10_env={parsed_data["pm10_env"]},'
                       f'pm25_env={parsed_data["pm25_env"]},'
                       f'pm100_env={parsed_data["pm100_env"]},'
                       f'part_03={parsed_data["part_03"]},'
                       f'part_05={parsed_data["part_05"]},'
                       f'part_10={parsed_data["part_10"]},'
                       f'part_25={parsed_data["part_25"]},'
                       f'part_50={parsed_data["part_50"]},'
                       f'part_100={parsed_data["part_100"]}'
                       f'date={parsed_data["date"]},'
                       f'time={parsed_data["time"]}')
            
            # Publish data to MQTT
            publish_data_to_mqtt(mqtt_client, data)

            # printing for reference
            # print("sent: " + message)

            # increment message index
            index += 1

        # Print received data in serial
        # print(f"Received: {data.strip()}")

        # Show received status in case CRC or header error occur
        status = LoRa.status()
        if status == LoRa.STATUS_CRC_ERR: 
            print("CRC error")
        elif status == LoRa.STATUS_HEADER_ERR: 
            print("Packet header error")

    except Exception as e:
        print(f"An error occurred: {e}")
        break

try:
    pass
except Exception as e:
    print(f"Error: {e}")
    LoRa.end()
