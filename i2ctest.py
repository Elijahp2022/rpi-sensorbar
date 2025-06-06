import smbus
import time

channel = 1
address = 0x3e
reg_write_dac = 0x40

bus = smbus.SMBus(channel)

#setBarStrobe()
barStrobe = 1
#clearInvertBits()
invertbits = 0

#reset() recreation
bus.write_byte_data(address, 0x7D, 0x12)
bus.write_byte_data(address, 0x7D, 0x34)

#begin() recreation, excluding reset() call
testRegisters = bus.read_word_data(address, 0x13)

if testRegisters == 0xFF00:
	bus.write_byte_data(address, 0x0F, 0xFF)
	bus.write_byte_data(address, 0x0E, 0xFC)
	bus.write_byte_data(address, 0x10, 0x01)
else:
	print("testing registers gone bad!")

while(1):
	#scan() recreation, excluding barstrobe checking
	bus.write_byte_data(address, 0x10, 0x02)
	time.sleep(0.002)
	bus.write_byte_data(address, 0x10, 0x00)

	lastBarRawvalue = bus.read_byte_data(address, 0x11)

	bus.write_byte_data(address, 0x10, 0x03)

	print(f"last bar raw value: {lastBarRawvalue}")
	time.sleep(0.1)
