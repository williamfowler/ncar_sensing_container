# Use the base image for ARM architecture with Python installed
FROM arm32v7/python:3.9

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
    && rm -rf /var/lib/apt/lists/*

