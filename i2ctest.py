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

def scan():
	bus.write_byte_data(address, 0x10, 0x02)
	time.sleep(0.002)
	bus.write_byte_data(address, 0x10, 0x00)

	lastBarRawValue = bus.read_byte_data(address, 0x11)

	bus.write_byte_data(address, 0x10, 0x03)
	return lastBarRawValue

def getPosition():
	accumulator = 0
	bitsCounted = 0
	i = 0

	rawBarValue = scan()

	# count active bits
	for i in range(8):
		if ((rawBarValue >> i) & 0x01) == 1:
			bitsCounted += 1

	i = 0

	# count negative position
	for i in range(7, 3, -1):
		if ((rawBarValue >> i) &0x01) == 1:
			accumulator += ((-32*(i-3))+1)

	i = 0
	# count positive position
	for i in range(4):
		if ((rawBarValue >> i) &0x01) == 1:
			accumulator += ((32*(4-i)-1))


	if bitsCounted > 0:
		positionValue = accumulator/bitsCounted

	else:
		positionValue = 0

	return int(positionValue)


def getDensity():
	bitsCounted = 0
	i = 0

	rawBarValue = scan()

	for i in range(8):
		if ((rawBarValue >> i) &0x01) == 1:
			bitsCounted += 1

	return bitsCounted
while(1):
	#scan() recreation, excluding barstrobe checking
	#bus.write_byte_data(address, 0x10, 0x02)
	#time.sleep(0.002)
	#bus.write_byte_data(address, 0x10, 0x00)

	#lastBarRawValue = bus.read_byte_data(address, 0x11)

	#bus.write_byte_data(address, 0x10, 0x03)
	lastBarRawValue = scan()
	print(f"last bar raw value: {hex(lastBarRawValue)}")
	print(f"position: {getPosition()}")
	print(f"density: {getDensity()}")
	
	# print binary value:
	for i in range(7, -1,-1):
		print((lastBarRawValue >> i) & 0x01, end="")
	print("b")

	time.sleep(0.500)
