TARGET := libvl53.so

SRC_FILES := \\
    vl53_reader.c \\
    vl53l0x_api.c \\
    vl53l0x_platform.c

CC := gcc
CFLAGS := -Wall -O2 -fPIC
LDFLAGS := -shared

$(TARGET): $(SRC_FILES)
	$(CC) $(CFLAGS) $(SRC_FILES) -o $(TARGET) $(LDFLAGS)