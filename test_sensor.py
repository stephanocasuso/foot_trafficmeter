import time
import board
import busio
import adafruit_vl53l0x

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the sensor
sensor = adafruit_vl53l0x.VL53L0X(i2c)

print("Sensor ready. Reading distance...")

try:
    while True:
        # Get the distance in millimeters
        distance = sensor.range
        print("Distance: {} mm".format(distance))
        time.sleep(0.5)  # adjust delay as needed
except KeyboardInterrupt:
    print("Test terminated.")