# Makefile for building libvl53.so from all SDK source files

CC = gcc
CFLAGS = -Wall -O2 -fPIC
INCLUDES = -Isource
SRCS = $(wildcard source/*.c)
OUT = libvl53.so

all: $(OUT)

$(OUT): $(SRCS)
	$(CC) $(CFLAGS) $(INCLUDES) $^ -o $@ -shared

clean:
	rm -f $(OUT)