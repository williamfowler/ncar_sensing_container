# Use the base image for ARM architecture with Python installed
FROM python:3.9

# Set environment variables to non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages for enabling serial port and SPI
RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    libffi-dev \
    libssl-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libreadline-dev \
    libbz2-dev \
    libsqlite3-dev \
    libz-dev \
    liblzma-dev \
    zlib1g-dev \
    build-essential \
    libudev-dev \
    libusb-1.0-0-dev \
    libpcap-dev \
    libgmp-dev \
    flex \
    bison \
    cmake \
    git \
    mosquitto \
    mosquitto-clients \
    nano \
    systemctl \
    iputils-ping \
    nmap \
    && rm -rf /var/lib/apt/lists/*

COPY lora /app/lora

# Set the working directory to the LoRa directory
WORKDIR /app/lora

# Install the Python package
RUN python setup.py install 

# Install additional Python packages
RUN pip install pytz \
    requests \
    board \
    adafruit-circuitpython-ltr390 \
    adafruit-circuitpython-bme680 \
    adafruit-circuitpython-pm25 \
    paho-mqtt

COPY LoRaRX.py \
    ltr390_example_MQTT.py \
    mqtt_publisher_example.py \
    on_start.sh \
    receive_and_save_updated.py \
    receive_and_save_mqtt.py \
    read_and_transmit.py \
    LoRaTX.py \
    /app/

COPY mqtt_setup /etc/mosquitto

# Set the working directory to the root of the repo
WORKDIR /app

EXPOSE 30001

# RUN chmod +x ./on_start.sh

# CMD ["sleep", "infinity"]
CMD ["python", "receive_and_save_mqtt.py"]