
import time
import board
import busio
import digitalio
from adafruit_vl53l0x import VL53L0X

"""
    Setting Sensor Addresses
    ~~~~~~~~~~~~~~~~~~~~~~~~

- The VL53L0X sensors only keep their I2C addresses until the Pi is powered off--resetting
them back to their default address of 0x29.
Due to this, their address must be set to unique values every time the Pi is powered on.

"""

# Configure XSHUT (shutdown) pins for each sensor
shutdown1 = digitalio.DigitalInOut(board.D4) # GPIO4
shutdown2 = digitalio.DigitalInOut(board.D5) # GPIO5
shutdown1.direction = shutdown2.direction = digitalio.Direction.OUTPUT

# Ensure both sensors are off initially
time.sleep(0.05)
shutdown1.value = False
shutdown2.value = False

time.sleep(0.05)  # brief pause after power down

# Initialize the I2C bus
i2c_bus = busio.I2C(board.SCL, board.SDA)

# Power up and address sensor 1 in GPIO4
shutdown1.value = True
time.sleep(0.1)
sensor1 = VL53L0X(i2c_bus)
sensor1.set_address(0x2A)

# Power up and address sensor 2 in GPIO5
time.sleep(0.05)
shutdown2.value = True
time.sleep(0.1)
sensor2 = VL53L0X(i2c_bus)
sensor2.set_address(0x2B)

print('Sensors initialized at addresses 0x2A and 0x2B. Starting sensor readings...')

# Poll loop: read and display distances every poll_interval (in seconds)
poll_interval = 0.5
try:
    while True:
        distance1 = sensor1.range
        distance2 = sensor2.range
        print(f'Sensor 1: {distance1} mm\t| Sensor 2: {distance2} mm')
        time.sleep(poll_interval)
except KeyboardInterrupt:
    print('\nTest terminated.')
