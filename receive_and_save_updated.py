import os
import sys
from LoRaRX import LoRa  # import LoRa module configured in LoRa.py
from datetime import datetime
import pytz # need sudo pip install pytz

# DCurrent timezone set to CST
tz = pytz.timezone('America/Chicago')

# Define the headers
headers = ("uv ambient_light "
          "temperuture gas humidity pressure altitude "
          "pm10_std pm25_std pm100_std pm10_env pm25_env pm100_env "
          "part_>_03 part_>_05 part_>_10 part_>_25 part_>_50 part_>_100 "
          "date time\n")

# Function to write headers if the file is empty or doesn't contain them
def write_headers_if_needed(file_path, headers):
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            file.write(headers)
    else:
        with open(file_path, "r") as file:
            first_line = file.readline().strip()
            if first_line != headers.strip():
                with open(file_path, "w") as file:
                    file.write(headers)

# Check and write headers if needed
file_path = "data.txt"
write_headers_if_needed(file_path, headers)

# Begin receiving loop
with open(file_path, "a") as file:
    while True:
        try:
            # Request for receiving new LoRa packet
            LoRa.request()
            # Wait for incoming LoRa packet
            LoRa.wait()

            # Put received packet to message variable
            message = ""
            while LoRa.available() > 0:
                message += chr(LoRa.read())

            # write the current date and time
            utc_now = datetime.now(pytz.utc) # current UTC time
            curr_time = utc_now.astimezone(tz) # convert to CST
            message += curr_time.strftime('%Y-%m-%d %H:%M:%S') + "\n"

            # Write received message to the file
            if message.strip():
                file.write(message)
                file.flush()

            # Print received message in serial
            print(f"Received: {message.strip()}")

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
