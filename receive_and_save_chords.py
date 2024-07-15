import os
import sys
import requests
from LoRaRX import LoRa  # import LoRa module configured in LoRa.py
from datetime import datetime
import pytz # need sudo pip install pytz

# DCurrent timezone set to CST
tz = pytz.timezone('America/Chicago')

# set these fields to the current info for your CHORDS account
CHORDS_url = "http://ec2-100-28-114-152.compute-1.amazonaws.com" # no trailing /
instrument_id = 1
user_email = "willi" + "amfo" + "wler04@" + "gmail.com"
api_key = "b1ow_nz5Qtz4vqsaTzVi"

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

def create_url(data_dict):
    base_url = "http://ec2-100-28-114-152.compute-1.amazonaws.com/measurements/url_create"
    query_params = [
        "instrument_id=1",
        f"uv={data_dict['uv']}",
        f"amb_light={data_dict['ambient_light']}",
        f"temp={data_dict['temperature']}",
        f"gas={data_dict['gas']}",
        f"humid={data_dict['humidity']}",
        f"pressure={data_dict['pressure']}",
        f"alt={data_dict['altitude']}",
        f"pm10={data_dict['pm10_std']}",
        f"pm25={data_dict['pm25_std']}",
        f"pm100={data_dict['pm100_std']}",
        f"pm10env={data_dict['pm10_env']}",
        f"pm25env={data_dict['pm25_env']}",
        f"pm100env={data_dict['pm100_env']}",
        f"part_03={data_dict['part_03']}",
        f"part_05={data_dict['part_05']}",
        f"part_10={data_dict['part_10']}",
        f"part_25={data_dict['part_25']}",
        f"part_50={data_dict['part_50']}",
        f"part_100={data_dict['part_100']}",
        f"at={data_dict['date']}T{data_dict['time']}",
        f"email={user_email}",
        f"api_key={api_key}"
    ]
    
    full_url = f"{base_url}?{'&'.join(query_params)}"
    return full_url

# Begin receiving loop
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

        # Write received data to the file
        if data.strip():

                # write the current date and time
            utc_now = datetime.now(pytz.utc) # current UTC time
            curr_time = utc_now.astimezone(tz) # convert to CST
            data += curr_time.strftime('%Y-%m-%d %H:%M:%S') + "\n"
            
            # parse data into dict
            parsed_data = parse_sensor_data(data)

            # create and send CHORDS url
            chords_url = create_url(parsed_data)
            response = requests.get(url=chords_url)
            print(response)

        # Print received data in serial
        print(f"Received: {data.strip()}")

        # Print packet/signal status including RSSI, SNR, and signalRSSI
        print("Packet status: RSSI = {0:0.2f} dBm | SNR = {1:0.2f} dB".format(LoRa.packetRssi(), LoRa.snr()))

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
