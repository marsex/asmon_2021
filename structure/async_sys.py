from structure import wifi, color
from time import sleep
import _thread
import network

th = _thread.start_new_thread

state={
    'wifi':'',
    'credentials':'',
    'cam':'',
    'data_host':'',
    'cam_host':''
}

def check_state(loop_delay):
    global state
    while True:
        state['credentials']=wifi.get_credentials()
        state['wifi']=network.WLAN(network.STA_IF).isconnected()
        
        sleep(loop_delay)

def get(key):
    return state[key]

def set(key,value):
    print('state['+key+']='+str(value))
    try:
        state[key]=value
        return True
    except:
        return False

def start():
    th(check_state, (1,))
    print(color.yellow()+'async status system running'+color.normal())