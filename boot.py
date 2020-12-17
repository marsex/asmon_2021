from machine import Pin
from time import sleep
print('Loading mainframe')
inp_gpio = [13, 15]
out_gpio = [2, 14, 12]

input_state = [Pin(i, Pin.IN).value() for i in inp_gpio]
output_state = [Pin(i, Pin.OUT).value() for i in out_gpio]

sleep(1)