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
    # Publish a message once connected
    client.publish("example/topic", payload="Hello, MQTT!", qos=1)

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

# Create a new MQTT client instance
client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)

# Assign the on_connect and on_publish callbacks
client.on_connect = on_connect
client.on_publish = on_publish

# Configure the client for a secure connection
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# Set username and password for authentication
client.username_pw_set("will", "PlayBallGame83")
# Connect to the MQTT broker
client.connect("0a611c2211104d4c82b15ec089b0ab68.s1.eu.hivemq.cloud", 8883)

# Start the network loop to process MQTT events
client.loop_start()

# Publish a message
client.publish("sensor/light", payload="trying the example code", qos=1)

# Keep the script running to ensure messages are sent
try:
    while True:
        pass
except KeyboardInterrupt:
    # Stop the network loop on interruption
    client.loop_stop()
    print("Disconnected")
