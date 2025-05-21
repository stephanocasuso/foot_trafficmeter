
#ifndef VL53_READER_H
#define VL53_READER_H

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Read the distance (in mm) from the specified sensor.
 * Sensor 0 = entry sensor (default I2C address: 0x29)
 * Sensor 1 = exit sensor (must be re-addressed to 0x30)
 *
 * Returns:
 *   - Distance in mm on success
 *   - -1 on failure
 */
int read_distance(int sensor_id);

/**
 * Initialize both sensors and configure them for long-range continuous mode.
 * Should be called once at boot or before first use.
 *
 * Returns:
 *   - 0 on success
 *   - -1 on failure
 */
int init_sensors();

#ifdef __cplusplus
}
#endif

#endif
