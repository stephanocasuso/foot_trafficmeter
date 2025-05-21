
SRC_DIR := source
TARGET := libvl53.so

SRC_FILES := \
	$(SRC_DIR)/vl53_reader.c \
	$(SRC_DIR)/vl53l0x_api.c \
	$(SRC_DIR)/vl53l0x_platform.c

# Include additional headers from source dir
INCLUDES := -I$(SRC_DIR)

CC := gcc
CFLAGS := -Wall -O2 -fPIC $(INCLUDES)
LDFLAGS := -shared

$(TARGET): $(SRC_FILES)
	$(CC) $(CFLAGS) $(SRC_FILES) -o $(TARGET) $(LDFLAGS)

clean:
	rm -f $(TARGET)
