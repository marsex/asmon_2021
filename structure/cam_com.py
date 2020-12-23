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

async def send_cam(to):
    await asyncio.sleep(1)
    print(color.blue()+'STARTING PYCOM CAM'+color.normal())
    await asyncio.sleep(1)
    while True:
        cam_server = sys_info.get('cam_server')
        cam_host = cam_server['host']
        port = cam_server['port']
        cam_address = cam_server['address']
        wifi_st = sys_info.get('wifi')
        wifi_st = sys_info.get('wifi')
        if wifi_st == False:
            await asyncio.sleep(3)
        if wifi_st != False:
            if cam_address == '':
                if cam_host != '':
                    try:
                        cam_address = socket.getaddrinfo(cam_host, port)[0][-1]
                        sys_info.setd('cam_server','address',cam_address)
                    except: 
                        cam_address = ''
                        print('Error getting CAM addr info')
                else:
                    print('cam_host not ready')
                    await asyncio.sleep(3)
            else:
                conn_try=0
                print(color.blue()+'{\n\tCONNECTING TO PYCOM CAM'+color.normal())
                try:
                    s = socket.socket()
                    s.setblocking(False)
                    connected = False
                    while connected == False:
                        try:
                            s.connect(cam_address)
                        except OSError as e:
                            if str(e) == "127":
                                connected = True
                                conn_try = 0
                            else:
                                conn_try = conn_try+1
                                if conn_try > to:
                                    print(color.red()+'\tCAM CONN F'+color.normal())
                                    conn_try = to
                                    break
                        await asyncio.sleep(.1)
                        pass
                    if conn_try != to:
                        print(color.blue()+'\tconnected to cam_address'+color.normal())
                        conn_try = 0
                        try:
                            n_try = 0
                            buf = False
                            cam.light('1')
                            while (n_try < 10 and buf == False): #{
                                # wait for sensor to start and focus before capturing image
                                print('\tgetting img')
                                buf = camera.capture()
                                if (buf == False): await asyncio.sleep(1)
                                n_try = n_try + 1
                            cam.light('0')
                            print('\tsending img:', len(buf))
                            while True:
                                try:             
                                    while buf:
                                        sent = s.send(buf)
                                        buf = buf[sent:]
                                    conn_try = 0
                                    break
                                except OSError as e:
                                    #print(e)
                                    if conn_try > to:
                                        print(color.red()+'CAM SEND F'+color.normal())
                                        break
                                    conn_try = conn_try+1
                                await asyncio.sleep(.1)
                            await asyncio.sleep(.1)
                            print('\timg sent')
                        except OSError as e:
                            print('\tsending cam failed '+str(e))
                    print(color.yellow()+'\tcam conn_try', conn_try)
                    print(color.red()+'\tcam out\n}\n'+color.normal())
                    sys_info.setd('cam_server','timeout',conn_try)
                    s.close()
                    del s
                except OSError as e:
                    print('cam socket failed',str(e))
        gc.collect()
        await asyncio.sleep(.1)
