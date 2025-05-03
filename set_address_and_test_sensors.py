#!/usr/bin/env python3
import time
import board
import busio
import digitalio
from adafruit_vl53l0x import VL53L0X

# Poll interval in seconds
poll_interval = 0.5

# Configure XSHUT (shutdown) pins for each sensor
shutdown1 = digitalio.DigitalInOut(board.D4)
shutdown2 = digitalio.DigitalInOut(board.D5)
shutdown1.direction = shutdown2.direction = digitalio.Direction.OUTPUT

# Ensure both sensors are off initially
time.sleep(0.05)
shutdown1.value = False
shutdown2.value = False

time.sleep(0.05)  # brief pause after power down

# Initialize the I2C bus
i2c_bus = busio.I2C(board.SCL, board.SDA)

# Power up and address sensor 1
shutdown1.value = True
time.sleep(0.1)
sensor1 = VL53L0X(i2c_bus)
sensor1.set_address(0x2A)

# Power up and address sensor 2
time.sleep(0.05)
shutdown2.value = True
time.sleep(0.1)
sensor2 = VL53L0X(i2c_bus)
sensor2.set_address(0x2B)

print('Sensors initialized at addresses 0x2A and 0x2B. Starting poll loop...')

# Poll loop: read and display distances
try:
    while True:
        dist1 = sensor1.range
        dist2 = sensor2.range
        print(f"Sensor 1: {dist1} mm\t| Sensor 2: {dist2} mm")
        time.sleep(poll_interval)
except KeyboardInterrupt:
    print('\nPolling stopped by user')
