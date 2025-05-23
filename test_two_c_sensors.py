import RPi.GPIO as GPIO
import time
from ctypes import CDLL, c_uint8, c_uint16, c_uint32, c_int, c_void_p

# Load C shared library
vl53 = CDLL('./libvl53.so')

# Set ctypes function signatures
vl53.VL53L0X_init.argtypes = [c_uint8]
vl53.VL53L0X_init.restype = c_void_p

vl53.VL53L0X_SetDeviceAddress.argtypes = [c_void_p, c_uint8]

vl53.VL53L0X_set_signal_rate_limit.argtypes = [c_void_p, c_uint16]
vl53.VL53L0X_set_sigma_limit.argtypes = [c_void_p, c_uint16]
vl53.VL53L0X_set_measurement_timing_budget.argtypes = [c_void_p, c_uint32]
vl53.VL53L0X_set_vcsel_pulse_period.argtypes = [c_void_p, c_uint8, c_uint8]
vl53.VL53L0X_start_ranging.argtypes = [c_void_p]
vl53.VL53L0X_get_distance.argtypes = [c_void_p]
vl53.VL53L0X_get_distance.restype = c_uint16

# I2C addresses
default_addr = 0x29
entry_sensor_addr = 0x30
exit_sensor_addr = 0x31

# GPIO pins connected to XSHUT
entry_xshut = 4  # GPIO4 -> entry sensor
exit_xshut = 5   # GPIO5 -> exit sensor

# Setup GPIO for XSHUT
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(entry_xshut, GPIO.OUT)
GPIO.setup(exit_xshut, GPIO.OUT)

# Reset both sensors
GPIO.output(entry_xshut, GPIO.LOW)
GPIO.output(exit_xshut, GPIO.LOW)
time.sleep(0.01)

# Power on entry sensor
GPIO.output(entry_xshut, GPIO.HIGH)
time.sleep(0.01)
entry_sensor = vl53.VL53L0X_init(default_addr)
if not entry_sensor:
    raise RuntimeError('Failed to initialize entry sensor.')
vl53.VL53L0X_SetDeviceAddress(entry_sensor, entry_sensor_addr << 1)

# Power on exit sensor
GPIO.output(exit_xshut, GPIO.HIGH)
time.sleep(0.01)
exit_sensor = vl53.VL53L0X_init(default_addr)
if not exit_sensor:
    raise RuntimeError('Failed to initialize exit sensor.')
vl53.VL53L0X_SetDeviceAddress(exit_sensor, exit_sensor_addr << 1)

# Long range mode config values
long_range_signal_limit = 0.1
long_range_sigma_limit = 60
long_range_timing_budget = 33000
long_range_vcsel_period = 18

# Configure both sensors for long-range mode
for sensor in [entry_sensor, exit_sensor]:
    vl53.VL53L0X_set_signal_rate_limit(sensor, int(long_range_signal_limit * (1 << 7)))
    vl53.VL53L0X_set_sigma_limit(sensor, int(long_range_sigma_limit))
    vl53.VL53L0X_set_measurement_timing_budget(sensor, long_range_timing_budget)
    vl53.VL53L0X_set_vcsel_pulse_period(sensor, 0, long_range_vcsel_period)
    vl53.VL53L0X_set_vcsel_pulse_period(sensor, 1, long_range_vcsel_period)
    vl53.VL53L0X_start_ranging(sensor)

print('Polling distances every 0.5 seconds. Press Ctrl+C to stop.\n')

try:
    while True:
        entry_distance = vl53.VL53L0X_get_distance(entry_sensor)
        exit_distance = vl53.VL53L0X_get_distance(exit_sensor)
        print(f'Entry sensor: {entry_distance} mm\tExit sensor: {exit_distance} mm')
        time.sleep(0.5)
except KeyboardInterrupt:
    print('\nStopping.')
finally:
    GPIO.cleanup()