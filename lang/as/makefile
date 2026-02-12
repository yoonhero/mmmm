AS = gcc
ASFLAGS = -m32 -g -nostdlib -static
TARGET = hello
SRC = hello.s

.PHONY: all clean debug server  

all: $(TARGET)

$(TARGET): $(SRC)
	$(AS) $(ASFLAGS) $(SRC) -o $(TARGET)

server: $(TARGET)
	@echo "Starting QEMU GDB server on port 1234..."
	qemu-i386 -g 1234 ./$(TARGET) &

debug: server
	gdb -ex "target remote :1234" -ex "layout asm" -ex "layout regs" ./$(TARGET)

clean:
	rm -f $(TARGET)