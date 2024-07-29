import paho.mqtt.client as paho
from LoRaRX import LoRa  # import LoRa module configured in LoRa.py
from datetime import datetime
import pytz  # need sudo pip install pytz

# MQTT Broker settings
MQTT_BROKER = "0a611c2211104d4c82b15ec089b0ab68.s1.eu.hivemq.cloud"
MQTT_PORT = 30001
MQTT_USERNAME = "will"
MQTT_PASSWORD = "PlayBallGame83"

# Initialize MQTT client
client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.tls_set()
client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_start()

# Current timezone set to CST
tz = pytz.timezone('America/Chicago')

# Begin receiving loop
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

        # Process and publish the message
        if message.strip():
            # Split the message into different sensor readings
            data = message.strip().split()

            # Assuming sensor readings are in a specific order
            topics = [
                "ltr390/uv",
                "ltr390/ambient_light",
                "bme680/temperature",
                "bme680/gas",
                "bme680/humidity",
                "bme680/pressure",
                "bme680/altitude",
                "pmsa003i/pm10_std",
                "pmsa003i/pm25_std",
                "pmsa003i/pm100_std",
                "pmsa003i/pm10_env",
                "pmsa003i/pm25_env",
                "pmsa003i/pm100_env",
                "pmsa003i/part_03",
                "pmsa003i/part_05",
                "pmsa003i/part_10",
                "pmsa003i/part_25",
                "pmsa003i/part_50",
                "pmsa003i/part_100"
            ]

            # Last part of the data is the station ID
            location = data[-1]

            # Publish each sensor reading to its corresponding topic in InfluxDB line protocol format
            for topic, value in zip(topics, data[:-1]):
                measurement = topic.split('/')[1]
                influx_message = f"{measurement},location={location} value={value}"
                client.publish(topic, payload=influx_message, qos=1)
                print(f"Published {influx_message} to {topic}")

            # Print received message and status
            utc_now = datetime.now(pytz.utc)  # current UTC time
            curr_time = utc_now.astimezone(tz)  # convert to CST
            print(f"Received: {message.strip()} at {curr_time.strftime('%Y-%m-%d %H:%M:%S')}")
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

client.loop_stop()
client.disconnect()
LoRa.end()
