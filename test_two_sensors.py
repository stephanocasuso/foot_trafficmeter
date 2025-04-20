import time
import board
import busio
from adafruit_vl53l0x import VL53L0X

# sensors' refresh rate in seconds
poll_interval = 0.5

# create i2c bus
i2cBus = busio.I2C(board.SCL, board.SDA)

# initialize sensor objects using their addresses
# the address set logic will be in the final sensor logic script
sensor1 = VL53L0X(i2cBus, address=0x2A)
sensor2 = VL53L0X(i2cBus, address=0x2B)

print('Starting two-sensor test.')

try:
    while True:
        distance1 = sensor1.range
        distance2 = sensor2.range
        print(f'Sensor 1: {distance1}mm \t| Sensor 2: {distance2}mm')
        time.sleep(poll_interval)
except KeyboardInterrupt:
    print('\nSensor monitoring stopped.')