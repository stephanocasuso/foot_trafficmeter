# Makefile for building libvl53.so on Raspberry Pi using ST VL53L0X SDK

CC = gcc
CFLAGS = -Wall -O2 -fPIC
INCLUDES = -Isource
OUT = libvl53.so

SRCS = \
    source/vl53_reader.c \
    source/vl53l0x_api.c \
    source/vl53l0x_api_calibration.c \
    source/vl53l0x_api_core.c \
    source/vl53l0x_api_ranging.c \
    source/vl53l0x_api_strings.c \
    source/vl53l0x_platform.c \
    source/vl53l0x_i2c_platform.c

all: $(OUT)

$(OUT): $(SRCS)
	$(CC) $(CFLAGS) $(INCLUDES) $^ -o $@ -shared

clean:
	rm -f $(OUT)