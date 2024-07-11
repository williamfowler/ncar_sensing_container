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
    strace \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository
# RUN git clone https://github.com/williamfowler/Waveshare_LoRa_setup.git /app

COPY lora /app/lora

# Set the working directory to the LoRa directory
WORKDIR /app/lora

# Install the Python package
RUN python setup.py install

# Install additional Python packages
RUN pip install pytz

# Copy your receive_and_save_updated.py script to the container
COPY receive_and_save_updated.py /app/receive_and_save_updated.py

COPY LoRaRX.py /app/LoRaRX.py

# Set the working directory to the root of the repo
WORKDIR /app

# Run the Python script
# CMD ["strace", "python", "receive_and_save_updated.py"]
CMD ["sleep", "infinity"]
# CMD ["python", "receive_and_save_updated.py"]