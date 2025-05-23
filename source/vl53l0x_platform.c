#include "vl53l0x_platform.h"
#include "vl53l0x_i2c_platform.h"
#include "vl53l0x_api.h"
#include <unistd.h>  // for usleep

#define VL53L0X_MAX_I2C_XFER_SIZE   64
#define I2C_BUFFER_CONFIG 1

#if I2C_BUFFER_CONFIG == 0
uint8_t i2c_global_buffer[VL53L0X_MAX_I2C_XFER_SIZE];
#define DECL_I2C_BUFFER
#define VL53L0X_GetLocalBuffer(Dev, n_byte)  i2c_global_buffer

#elif I2C_BUFFER_CONFIG == 1
#define DECL_I2C_BUFFER  uint8_t LocBuffer[VL53L0X_MAX_I2C_XFER_SIZE];
#define VL53L0X_GetLocalBuffer(Dev, n_byte)  LocBuffer

#elif I2C_BUFFER_CONFIG == 2
#define DECL_I2C_BUFFER

#else
#error "invalid I2C_BUFFER_CONFIG"
#endif

#define VL53L0X_GetI2CAccess(Dev)
#define VL53L0X_DoneI2CAcces(Dev)

VL53L0X_Error VL53L0X_LockSequenceAccess(VL53L0X_DEV Dev) {
    return VL53L0X_ERROR_NONE;
}

VL53L0X_Error VL53L0X_UnlockSequenceAccess(VL53L0X_DEV Dev) {
    return VL53L0X_ERROR_NONE;
}

VL53L0X_Error VL53L0X_WriteMulti(VL53L0X_DEV Dev, uint8_t index, uint8_t *pdata, uint32_t count) {
    if (count >= VL53L0X_MAX_I2C_XFER_SIZE)
        return VL53L0X_ERROR_INVALID_PARAMS;

    int32_t status = VL53L0X_write_multi(Dev->I2cDevAddr, index, pdata, count);
    return status ? VL53L0X_ERROR_CONTROL_INTERFACE : VL53L0X_ERROR_NONE;
}

VL53L0X_Error VL53L0X_ReadMulti(VL53L0X_DEV Dev, uint8_t index, uint8_t *pdata, uint32_t count) {
    if (count >= VL53L0X_MAX_I2C_XFER_SIZE)
        return VL53L0X_ERROR_INVALID_PARAMS;

    int32_t status = VL53L0X_read_multi(Dev->I2cDevAddr, index, pdata, count);
    return status ? VL53L0X_ERROR_CONTROL_INTERFACE : VL53L0X_ERROR_NONE;
}

VL53L0X_Error VL53L0X_WrByte(VL53L0X_DEV Dev, uint8_t index, uint8_t data) {
    int32_t status = VL53L0X_write_byte(Dev->I2cDevAddr, index, data);
    return status ? VL53L0X_ERROR_CONTROL_INTERFACE : VL53L0X_ERROR_NONE;
}

VL53L0X_Error VL53L0X_WrWord(VL53L0X_DEV Dev, uint8_t index, uint16_t data) {
    int32_t status = VL53L0X_write_word(Dev->I2cDevAddr, index, data);
    return status ? VL53L0X_ERROR_CONTROL_INTERFACE : VL53L0X_ERROR_NONE;
}

VL53L0X_Error VL53L0X_WrDWord(VL53L0X_DEV Dev, uint8_t index, uint32_t data) {
    int32_t status = VL53L0X_write_dword(Dev->I2cDevAddr, index, data);
    return status ? VL53L0X_ERROR_CONTROL_INTERFACE : VL53L0X_ERROR_NONE;
}

VL53L0X_Error VL53L0X_UpdateByte(VL53L0X_DEV Dev, uint8_t index, uint8_t AndData, uint8_t OrData) {
    uint8_t data;
    int32_t status = VL53L0X_read_byte(Dev->I2cDevAddr, index, &data);
    if (status) return VL53L0X_ERROR_CONTROL_INTERFACE;

    data = (data & AndData) | OrData;
    status = VL53L0X_write_byte(Dev->I2cDevAddr, index, data);
    return status ? VL53L0X_ERROR_CONTROL_INTERFACE : VL53L0X_ERROR_NONE;
}

VL53L0X_Error VL53L0X_RdByte(VL53L0X_DEV Dev, uint8_t index, uint8_t *data) {
    int32_t status = VL53L0X_read_byte(Dev->I2cDevAddr, index, data);
    return status ? VL53L0X_ERROR_CONTROL_INTERFACE : VL53L0X_ERROR_NONE;
}

VL53L0X_Error VL53L0X_RdWord(VL53L0X_DEV Dev, uint8_t index, uint16_t *data) {
    int32_t status = VL53L0X_read_word(Dev->I2cDevAddr, index, data);
    return status ? VL53L0X_ERROR_CONTROL_INTERFACE : VL53L0X_ERROR_NONE;
}

VL53L0X_Error VL53L0X_RdDWord(VL53L0X_DEV Dev, uint8_t index, uint32_t *data) {
    int32_t status = VL53L0X_read_dword(Dev->I2cDevAddr, index, data);
    return status ? VL53L0X_ERROR_CONTROL_INTERFACE : VL53L0X_ERROR_NONE;
}

#include <unistd.h>  // for usleep
VL53L0X_Error VL53L0X_PollingDelay(VL53L0X_DEV Dev) {
    usleep(1000);  // 1 ms delay
    return VL53L0X_ERROR_NONE;
}