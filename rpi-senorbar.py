'''
rpi-sensorbar.py
Contributer(s): Elijah Polyakov
Written: 2025-06-06
Updated: 2025-06-06

Python library for using the Sparkfun line follower sensor array with RPI.
Includes code for controlling the sensor array as well as the circular buffer.
'''

import smbus #for I2C
import time #for delays

class sensor_bar():
    def __init__(self, address):
        self.address = address
        self.invert_bits = 0
        self.bar_strobe = 0
        self.bus = smbus.SMBus(1)
    
    def begin(self):

        self.reset()
        test_registers = self.bus.read_word_data(self.address, 0x13)

        if test_registers == 0xFF00:
            self.bus.write_byte_data(self.address, 0x0F, 0xFF)
            self.bus.write_byte_data(self.address, 0x0E, 0xFC)
            self.bus.write_byte_data(self.address, 0x10, 0x01)
        else:
            print("testing registers gone bad!")
    
    def reset(self):
        self.bus.write_byte_data(self.address, 0x7D, 0x12)
        self.bus.write_byte_data(self.address, 0x7D, 0x34)

    def scan(self):

        if self.bar_strobe == 1:
            self.bus.write_byte_data(self.address, 0x10, 0x02)
            time.sleep(0.002)
            self.bus.write_byte_data(self.address, 0x10, 0x00)
        
        else:
            self.bus.write_byte_data(self.address, 0x10, 0x00)

        last_bar_raw_value = self.bus.read_byte_data(self.address, 0x11)

        if self.invert_bits == 1:
            last_bar_raw_value ^= 0xFF
        
        if self.bar_strobe == 1:
            self.bus.write_byte_data(self.address, 0x10, 0x03)

        return last_bar_raw_value
    
    def getPosition(self):
        accumulator = 0
        bits_counted = 0
        i = 0

        raw_bar_value = self.scan()

        # count active bits
        for i in range(8):
            if ((raw_bar_value >> i) & 0x01) == 1:
                bits_counted += 1

        i = 0

        # count negative position
        for i in range(7, 3, -1):
            if ((raw_bar_value >> i) &0x01) == 1:
                accumulator += ((-32*(i-3))+1)

        i = 0
        # count positive position
        for i in range(4):
            if ((raw_bar_value >> i) &0x01) == 1:
                accumulator += ((32*(4-i)-1))


        if bits_counted > 0:
            position_value = accumulator/bits_counted

        else:
            position_value = 0

        return int(position_value)
    
    def get_density(self):
        bits_counted = 0
        i = 0

        raw_bar_value = self.scan()

        for i in range(8):
            if ((raw_bar_value >> i) &0x01) == 1:
                bits_counted += 1

        return bits_counted
    
    def set_bar_strobe(self):
        self.bar_strobe = 1
    
    def clear_bar_strobe(self):
        self.bar_strobe = 0
    
    def set_invert_bits(self):
        self.invert_bits = 1
    
    def clear_invert_bits(self):
        self.invert_bits = 0


    '''
    Circular Buffer:
    '''

class circular_buffer():
    def __init__(self, input_size):
        self.data = [0]*input_size
        self.last_pointer = 0
        self.elements_used = 0
        self.size = input_size

    def get_element(self, element_num):
        virtual_element_num = self.last_pointer - element_num
        if virtual_element_num < 0:
            virtual_element_num += self.size
        
        return self.data[virtual_element_num]
    
    def push_element(self, element_val):
        self.last_pointer += 1

        if self.last_pointer >= self.size:
            self.last_pointer = 0

        self.data[self.last_pointer] = element_val

        if self.elements_used < self.size:
            self.elements_used += 1
        
    def average_last(self, num_elements):
        accumulator = 0
        
        for i in range(num_elements):
            accumulator += self.get_element(i)
        
        accumulator /= num_elements

        return accumulator
    

    def record_length(self):
        return self.elements_used