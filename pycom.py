from structure import machine_data, color, cam, wifi, sys_info, update
from structure import headers as hdr
from time import sleep
import uasyncio as asyncio
import network
import uselect
import camera
import socket
import uerrno
import json
import gc
import machine

wifi.ap_on()
wifi.scan_networks()

cam.start()

json_command={}

def start(to):
    if sys_info.restore() == False:
        sys_info.reset()
    try:
        main_loop = asyncio.new_event_loop()
        main_loop.create_task(check_state(2))
        main_loop.create_task(send_data(to))
        main_loop.create_task(send_cam(to))
        main_loop.create_task(ap_cam(to))
        main_loop.create_task(ap_sv(to))
        main_loop.run_forever()
    except OSError as e:
        print("async failed"+str(e)) 
    print("async out")   
    gc.collect()
    gc.mem_free()
    machine.reset()

start(50)