from structure import wifi, color
from time import sleep
import network

state={
    'wifi':'',
    'credentials':'',
    'cam':'',
    'data_host':'',
    'cam_host':''
}

def get(key):
    return state[key]

def set(key,value):
    print('state['+key+']='+str(value))
    try:
        state[key]=value
        return True
    except:
        return False