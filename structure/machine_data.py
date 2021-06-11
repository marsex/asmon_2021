import machine
import time
import uerrno
from machine import Pin
from structure import update

inp_gpio = [13, 15]
out_gpio = [2, 14, 12]

machine_data = {
    "command":{'command':'wait'},
    "uptime": str(time.time()),
    "board":"ESP-CAMv1.0",
    "user": "EMAIL",
    "psw": "123",
    "id":"CAMARA 02",
    "gpio": {
        "input_state": [0, 0],
        "output_state": [0, 0, 0]
    }
}

def gpio_pins():
    return out_gpio, inp_gpio

def out_pins():
    return out_gpio

def inp_pins():
    return inp_gpio

def parse_data(command_json):
    if command_json['command'] == 'output_state':
        print(command_json['data']['pin'])
        print(command_json['data']['value'])
        pin = int(command_json['data']['pin'])
        state = int(command_json['data']['value'])
        command = {'command':'output_updated','data':{'pin':pin,'state':state}}
        set('command',command)
        Pin(out_gpio[pin]).value(state)

def set_double(arg1, arg2, arg3):
    global machine_data
    try:
        machine_data[arg1][arg2] = arg3
    except:
        return 'error manipulating machine data, \narg1:', arg1, '\narg2:', arg2, '\narg3:', arg3

def set(key,arg):
    global machine_data
    try:
        machine_data[key] = arg
        return True
    except:
        return False

def get():
    global machine_data
    input_state = [Pin(i, Pin.IN).value() for i in inp_gpio]
    output_state = [Pin(i, Pin.OUT).value() for i in out_gpio]
    machine_data['uptime'] = str(time.time())
    machine_data['gpio']['input_state'] = input_state   
    machine_data['gpio']['output_state'] = output_state
    return machine_data
 
def get_key(key):
    return machine_data[key]

def timbre_event(pin):
    timbre.irq(trigger=Pin.IRQ_RISING, handler=None)
    if pin.value():
        machine_data['command'] = {'command':'event','name':'timbre'}
        print('timbre event',pin.value())
    timbre.irq(trigger=Pin.IRQ_RISING, handler=timbre_event)

def sensor_event(pin):
    timbre.irq(trigger=Pin.IRQ_RISING, handler=None)
    if pin.value():
        machine_data['command'] = {'command':'event','name':'sensor'}
        print('sensor event',pin.value())
    sensor.irq(trigger=Pin.IRQ_RISING, handler=sensor_event)
   
timbre = Pin(inp_gpio[0], Pin.IN)
sensor = Pin(inp_gpio[1], Pin.IN)

timbre.irq(trigger=Pin.IRQ_RISING, handler=timbre_event)
sensor.irq(trigger=Pin.IRQ_RISING, handler=sensor_event)