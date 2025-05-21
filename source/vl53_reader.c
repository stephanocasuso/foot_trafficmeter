
#include "vl53_reader.h"
#include "vl53l0x_api.h"
#include "vl53l0x_platform.h"
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#define ENTRY_SENSOR_ADDR 0x29
#define EXIT_SENSOR_ADDR  0x30

static VL53L0X_Dev_t entry_sensor = { .I2cDevAddr = ENTRY_SENSOR_ADDR };
static VL53L0X_Dev_t exit_sensor  = { .I2cDevAddr = EXIT_SENSOR_ADDR };
static VL53L0X_Dev_t* sensors[2] = { &entry_sensor, &exit_sensor };

int init_sensor(VL53L0X_Dev_t* dev) {
    VL53L0X_DeviceInfo_t info;
    int status;

    dev->comms_type = 1; // I2C
    dev->comms_speed_khz = 400;

    status = VL53L0X_WaitDeviceBooted(dev);
    if (status) return -1;

    status = VL53L0X_DataInit(dev);
    if (status) return -1;

    status = VL53L0X_GetDeviceInfo(dev, &info);
    if (status) return -1;

    status = VL53L0X_StaticInit(dev);
    if (status) return -1;

    // Long-range mode
    status = VL53L0X_SetLimitCheckEnable(dev, VL53L0X_CHECKENABLE_SIGMA_FINAL_RANGE, 1);
    status |= VL53L0X_SetLimitCheckEnable(dev, VL53L0X_CHECKENABLE_SIGNAL_RATE_FINAL_RANGE, 1);
    status |= VL53L0X_SetLimitCheckValue(dev, VL53L0X_CHECKENABLE_SIGNAL_RATE_FINAL_RANGE, (FixPoint1616_t)(0.1*65536));
    status |= VL53L0X_SetLimitCheckValue(dev, VL53L0X_CHECKENABLE_SIGMA_FINAL_RANGE, (FixPoint1616_t)(60*65536));
    status |= VL53L0X_SetMeasurementTimingBudgetMicroSeconds(dev, 33000);
    status |= VL53L0X_SetVcselPulsePeriod(dev, VL53L0X_VCSEL_PERIOD_PRE_RANGE, 18);
    status |= VL53L0X_SetVcselPulsePeriod(dev, VL53L0X_VCSEL_PERIOD_FINAL_RANGE, 14);

    if (status) return -1;

    // Start continuous mode
    status = VL53L0X_StartMeasurement(dev);
    if (status) return -1;

    return 0;
}

int init_sensors() {
    if (init_sensor(&entry_sensor) != 0) return -1;
    if (init_sensor(&exit_sensor) != 0) return -1;
    return 0;
}

int read_distance(int sensor_id) {
    if (sensor_id < 0 || sensor_id > 1) return -1;

    VL53L0X_Dev_t* dev = sensors[sensor_id];
    VL53L0X_RangingMeasurementData_t data;

    int status = VL53L0X_PerformSingleRangingMeasurement(dev, &data);
    if (status || data.RangeStatus != 0) {
        return -1;
    }

    return data.RangeMilliMeter;
}
