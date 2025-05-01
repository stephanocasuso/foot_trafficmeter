
"""
    Setting Sensor Addresses
    ~~~~~~~~~~~~~~~~~~~~~~~~

- The VL53L0X sensors only keep their I2C addresses until the Pi is powered off--resetting
them back to their default address of 0x29.
Due to this, their address must be set to unique values every time the Pi is powered on.

- This code will eventually be embedded into the final script
"""

import time
import board, busio, digitalio
from adafruit_vl53l0x import VL53L0X

# config sensor XSHUT pins
sh1 = digitalio.DigitalInOut(board.D4)
sh2 = digitalio.DigitalInOut(board.D5)
sh1.direction = sh2.direction = digitalio.Direction.OUTPUT

# turn both XSHUT pins off
sh1.value = False
sh2.value = False
time.sleep(0.1) # 100ms delay allows for pin firmware to catch up

# boot up sensor 1, set to 0x2A
# default address is 0x29 (41), so 0x2A is 1 unit higher than that (42)
sh1.value = True
time.sleep(0.1)
i2c = busio.I2C(board.SCL, board.SDA)
sensor1 = VL53L0X(i2c)
sensor1.set_address(0x2A)
print('Sensor 1 now at address 0x2A')

# set sensor 2 to 0x2B (43)
sh2.value = True
time.sleep(0.1)
sensor2 = VL53L0X(i2c)
sensor2.set_address(0x2B)
print('Sensor 2 now at address 0x2B')
