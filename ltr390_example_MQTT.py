import time
import board
import busio
import adafruit_ltr390
import paho.mqtt.client as paho
from paho import mqtt

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc, properties=None):
    """
    Prints the result of the connection with a reason code.
    
    :param client: The client instance.
    :param userdata: User-defined data.
    :param flags: Response flags from the broker.
    :param rc: Connection result code.
    :param properties: MQTTv5 properties (optional).
    """
    print("Connected with result code " + str(rc))

# Callback when a message is successfully published
def on_publish(client, userdata, mid, properties=None):
    """
    Prints the message ID to confirm successful publication.
    
    :param client: The client instance.
    :param userdata: User-defined data.
    :param mid: Message ID of the published message.
    :param properties: MQTTv5 properties (optional).
    """
    print("Message ID: " + str(mid))

# Initialize MQTT client
client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect
client.on_publish = on_publish

# Configure the client for a secure connection
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set("will", "PlayBallGame83")
client.connect("0a611c2211104d4c82b15ec089b0ab68.s1.eu.hivemq.cloud", 8883)

# Initialize the sensor
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_ltr390.LTR390(i2c)

# Start the MQTT client loop
client.loop_start()

try:
    while True:
        # Read ambient light data
        light_value = sensor.light
        # Publish the light value to the MQTT topic
        client.publish("sensor/light", payload=str(light_value), qos=1)
        print(f"Published ambient light value: {light_value}")
        
        # Wait before the next reading
        time.sleep(60)  # Adjust the delay as needed (in seconds)

except KeyboardInterrupt:
    # Stop the MQTT client loop on interruption
    client.loop_stop()
    print("Disconnected")

