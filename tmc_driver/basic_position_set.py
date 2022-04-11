#!/usr/bin/python
# coding = utf-8


import spidev
import time

# We only have SPI bus 0 available to us on the Pi
bus = 0

#Device is the chip select pin. Set to 0 or 1, depending on the connections
device = 0
# Enable SPI
spi = spidev.SpiDev()
# Open a connection to a specific bus and device (chip select pin)
spi.open(bus, device)
# Set SPI speed and mode
spi.max_speed_hz = 500000
spi.mode = 0


# Read GSTAT to clear reset flag
data = [0x01, 0x00, 0x00, 0x00, 0x00]
response = spi.xfer(data)

# Write chopper configs 0x6C
data = [0xEC, 0x00, 0x01, 0x00, 0xC5]
response = spi.xfer(data)

# Write IRUN=10 IHOLD=2 0x10
data = [0x90, 0x00, 0x06, 0x0A, 0x02]
response = spi.xfer(data)

# Write - Set RAMPMODE to 1 (Velocity mode) 0x20
data = [0xA0, 0x00, 0x00, 0x00, 0x01]
response = spi.xfer(data)


# A1 = 1, first acceleration
data = [0xA4, 0x00, 0x00, 0x03, 0xE8]
response = spi.xfer(data)

# V1 = 50000 Acceleration threshold velocity
data = [0xA5, 0x00, 0x00, 0xC3, 0x50]
response = spi.xfer(data)

# AMAX = 500 acceleration above V1
data = [0xA6, 0x00, 0x00, 0x01, 0xF4]
response = spi.xfer(data)

# VMAX = 200000
data = [0xA7, 0x00, 0x03, 0x0D, 0x40]
response = spi.xfer(data)

# DMAX = 700 deceleration above V1
data = [0xA8, 0x00, 0x00, 0x02, 0xBC]
response = spi.xfer(data)

# D1 = 1400 deceleration below V1
data = [0xAA, 0x00, 0x00, 0x05, 0x78]
response = spi.xfer(data)

# VSTOP = 10 stop velocity (near to 0)
data = [0xAB, 0x00, 0x00, 0x00, 0x0A]
response = spi.xfer(data)

# RAMPMODE = 0 (Target position move)
data = [0xA0, 0x00, 0x00, 0x00, 0x00]
response = spi.xfer(data)

# Move
# XTRAGET = move to left
# 00 07 D0 00
data = [0xAD, 0x00, 0x07, 0xD0, 0x00]
response = spi.xfer(data)


# Read actual position XACTUAL
data = [0x21, 0x00, 0x00, 0x00, 0x00]
response = spi.xfer(data)
print(f"XACTUAL position:{response}")

