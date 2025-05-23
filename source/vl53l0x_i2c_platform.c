
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include "vl53l0x_i2c_platform.h"

#define I2C_DEVICE "/dev/i2c-1"

int i2c_fd = -1;

int32_t VL53L0X_write_multi(uint8_t address, uint8_t index, uint8_t *pdata, int32_t count) {
    uint8_t buffer[count + 1];
    buffer[0] = index;
    for (int i = 0; i < count; i++) {
        buffer[i + 1] = pdata[i];
    }

    if (ioctl(i2c_fd, I2C_SLAVE, address) < 0) return -1;
    if (write(i2c_fd, buffer, count + 1) != count + 1) return -1;
    return 0;
}

int32_t VL53L0X_read_multi(uint8_t address, uint8_t index, uint8_t *pdata, int32_t count) {
    if (ioctl(i2c_fd, I2C_SLAVE, address) < 0) return -1;
    if (write(i2c_fd, &index, 1) != 1) return -1;
    if (read(i2c_fd, pdata, count) != count) return -1;
    return 0;
}

int32_t VL53L0X_write_byte(uint8_t address, uint8_t index, uint8_t data) {
    return VL53L0X_write_multi(address, index, &data, 1);
}

int32_t VL53L0X_write_word(uint8_t address, uint8_t index, uint16_t data) {
    uint8_t buffer[2];
    buffer[0] = data >> 8;
    buffer[1] = data & 0xFF;
    return VL53L0X_write_multi(address, index, buffer, 2);
}

int32_t VL53L0X_write_dword(uint8_t address, uint8_t index, uint32_t data) {
    uint8_t buffer[4];
    buffer[0] = (data >> 24) & 0xFF;
    buffer[1] = (data >> 16) & 0xFF;
    buffer[2] = (data >> 8) & 0xFF;
    buffer[3] = data & 0xFF;
    return VL53L0X_write_multi(address, index, buffer, 4);
}

int32_t VL53L0X_read_byte(uint8_t address, uint8_t index, uint8_t *pdata) {
    return VL53L0X_read_multi(address, index, pdata, 1);
}

int32_t VL53L0X_read_word(uint8_t address, uint8_t index, uint16_t *pdata) {
    uint8_t buffer[2];
    int status = VL53L0X_read_multi(address, index, buffer, 2);
    *pdata = ((uint16_t)buffer[0] << 8) | buffer[1];
    return status;
}

int32_t VL53L0X_read_dword(uint8_t address, uint8_t index, uint32_t *pdata) {
    uint8_t buffer[4];
    int status = VL53L0X_read_multi(address, index, buffer, 4);
    *pdata = ((uint32_t)buffer[0] << 24) | ((uint32_t)buffer[1] << 16) | ((uint32_t)buffer[2] << 8) | buffer[3];
    return status;
}

int32_t VL53L0X_comms_initialise(uint8_t comms_type, uint16_t comms_speed_khz) {
    i2c_fd = open(I2C_DEVICE, O_RDWR);
    return (i2c_fd >= 0) ? 0 : -1;
}

int32_t VL53L0X_comms_close(void) {
    if (i2c_fd >= 0) close(i2c_fd);
    i2c_fd = -1;
    return 0;
}
