CC ?= cc
CFLAGS ?= -O2 -std=c11 -Wall -Wextra -pedantic

TARGET := bfcc
SRC := bfcc.c

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET)

clean:
	rm -f $(TARGET)
