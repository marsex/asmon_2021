import machine
import dht
import time
import uerrno
from machine import Pin
from structure import update

inp_gpio = [13, 15]
out_gpio = [2, 14, 12]

machine_data = {
    "command": "null",
    "version": "v0.9.1.1",
    "platform": "asmon",
    "uptime": str(time.time()),
    "user": "dev_cam01",
    "gpio": {
        "input_enable": [0, 0, 1, 0, 0, 0, 0, 0],
        "input_state": [0, 0, 1, 0, 0, 0, 0, 0],
        "input_prog": [0, 0, 2, 0, 0, 0, 0, 0],
        "output_enable": [1, 1, 1, 1, 1, 1, 1, 1],
        "output_state": [0, 0, 0, 0, 0, 1, 0, 0],
        "output_prog": [0, 0, 0, 0, 0, 0, 0, 0]
    },
    "dht1": {
        "tmp_enable": 0,
        "tmp": 0,
        "tmp_salida": 3,
        "tmp_set": 0,
        "tmp_on_time": 0,
        "tmp_on_tick": 0,
        "tmp_off_time": 0,
        "tmp_off_tick": 0,
        "tmp_interval": 0,
        "tmp_tick": 0,
        "hmd_enable": 0,
        "hmd": 0,
        "hmd_salida": 3,
        "hmd_set": 0,
        "hmd_on_time": 0,
        "hmd_on_tick": 0,
        "hmd_off_time": 0,
        "hmd_off_tick": 0,
        "hmd_interval": 0,
        "hmd_tick": 0
    },
    "dht2": {
        "tmp_enable": 0,
        "tmp": 0,
        "tmp_salida": 3,
        "tmp_set": 0,
        "tmp_on_time": 0,
        "tmp_on_tick": 0,
        "tmp_off_time": 0,
        "tmp_off_tick": 0,
        "tmp_interval": 0,
        "tmp_tick": 0,
        "hmd_enable": 0,
        "hmd": 0,
        "hmd_salida": 3,
        "hmd_set": 0,
        "hmd_on_time": 0,
        "hmd_on_tick": 0,
        "hmd_off_time": 0,
        "hmd_off_tick": 0,
        "hmd_interval": 0,
        "hmd_tick": 0
    }
}
def gpio_pins():
    return out_gpio, inp_gpio


def out_pins():
    return out_gpio


def inp_pins():
    return inp_gpio


def set_double(arg1, arg2, arg3):
    global machine_data
    try:
        machine_data[arg1][arg2] = arg3
    except:
        return 'error manipulating machine data, \narg1:', arg1, '\narg2:', arg2, '\narg3:', arg3


def parse_data(command_json):
    # print(client_data)
    # try:
    #parsed_input = str(client_data[2:len(client_data)-1].replace("\'", "\""))
    # print(parsed_input)
    #command_json = ujson.loads(client_data)
    #print(command_json)
    #print('got command')

    if command_json['command'] == 'output_state':
        data = command_json['update'].split('=')
        pin = int(data[0])-1
        state = int(data[1])
        out_gpio = out_pins()
        Pin(out_gpio[pin], value=state)
    elif command_json['command'] == 'dht1':
        data = command_json['update'].split(',')
        print(data)
        for x in data:
            objeto = x.split('=')
            set_double('dht1', objeto[0], objeto[1])
    elif command_json['command'] == 'remote_update':
        update_info = command_json['update'].split(',')
        print('try to update', update_info)
        update.remote(update_info[0], update_info[1], update_info[2])
    # except:
    #print('error reading json')


def get():
    global machine_data
    input_state = [Pin(i, Pin.IN).value() for i in inp_gpio]
    output_state = [Pin(i, Pin.OUT).value() for i in out_gpio]
    machine_data['dht1']['tmp'] = 0  # dht1.temperature()
    machine_data['dht1']['hmd'] = 0  # dht1.humidity()
    machine_data['dht2']['tmp'] = 0  # dht2.temperature()
    machine_data['dht2']['hmd'] = 0  # dht2.humidity()
    machine_data['uptime'] = str(time.time())
    machine_data['gpio']['input_state'] = input_state   
    machine_data['gpio']['output_state'] = output_state
    return machine_data