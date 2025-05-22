# List of source files to include, excluding Windows-only files
SRCS = \
    source/vl53_reader.c \
    source/vl53l0x_api.c \
    source/vl53l0x_api_calibration.c \
    source/vl53l0x_api_core.c \
    source/vl53l0x_api_ranging.c \
    source/vl53l0x_api_strings.c

# Compiler setup
CC = gcc
CFLAGS = -Wall -O2 -fPIC
INCLUDES = -Isource
OUT = libvl53.so

all: $(OUT)

$(OUT): $(SRCS)
	$(CC) $(CFLAGS) $(INCLUDES) $^ -o $@ -shared

clean:
	rm -f $(OUT)