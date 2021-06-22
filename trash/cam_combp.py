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

async def start(to):
    await asyncio.sleep(.12)
    print(color.blue()+'STARTING PYCOM CAM'+color.normal())
    await asyncio.sleep(1)
    while True:
        cam_server = sys_info.get('cam_server')
        cam_host = cam_server['host']
        port = cam_server['port']
        cam_address = cam_server['address']
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
                            else:
                                conn_try = conn_try+1
                                if conn_try > to:
                                    print(color.red()+'\tCAM CONN F'+color.normal())
                                    conn_try = to
                                    break
                        await asyncio.sleep(.1)
                        pass
                    #connected
                    if conn_try < to:
                        print(color.blue()+'\tconnected to cam_address'+color.normal())
                        
                        print('\tsending img')
                        img_data = {'user':machine_data.get_key('user'),'id':machine_data.get_key('id')}
                        id_data = json.dumps(img_data)
                        s.send(id_data.encode())
                        conn_try = 0
#s                    |   |   |   |
                        #0#1#2
#s                    |   |   |   |
                        while True:
                            if conn_try > to:
                                print('\n\tcouldnt send picture')
                                break
                            frame = False
                            cam.light('1')
                            print('\tgetting img')
                            frame = camera.capture()
                            cam.light('0')
                            
#s                    |   |   |   |
                        #0#1#2
#s                    |   |   |   |
                            print('\n\tsending img')
                            while True:
                                try:
                                    while frame:
                                        sent = s.send(frame)
                                        frame = frame[sent:]
                                        await asyncio.sleep(.01)
                                    print('\timg sent')
                                    break
                                except OSError as e:
                                    if conn_try > to:
                                        print(color.red()+'CAM SEND F'+color.normal())
                                        conn_try = 0
                                        break
                                    conn_try = conn_try+1
                                    await asyncio.sleep(.1)
#s                    |   |   |   |
                        #0#1#2
#s                    |   |   |   |
                            print('\tsending end line')
                            data = json.dumps({'command':'imgsent'})
                            data = data.encode()
                            while True:
                                try:
                                    while data:
                                        sent = s.send(data)
                                        data = data[sent:]
                                    conn_try = 0
                                    print('\tdata sent')
                                    machine_data.set('command',{'command':'wait'})
                                    break
                                except OSError as e:
                                    if conn_try > to:
                                        print(color.red()+'DATA SEND F'+color.normal())
                                        break
                                    conn_try = conn_try+1
                                    await asyncio.sleep(.1)   
#s                    |   |   |   |
                        #0#1#2
#s                    |   |   |   |
                            print('\treceiving CAM server data')
                            while True:
                                try:
                                    res = s.recv(256)
                                    await asyncio.sleep(.01)
                                    if str(res).find('command') != -1:
                                        print('\tCAM server data received: ')
                                        print(res)
                                        conn_try = 0
                                        break
                                    if conn_try > to*10:
                                        print(color.red()+'\tCAM RECV F'+color.normal())
                                        break
                                    conn_try = conn_try + 1
                                except OSError as e:
                                    if conn_try > to:
                                        print(color.red()+'\tERROR CAM RECV F'+color.normal())
                                        break
                                    conn_try = conn_try + 1
                                    await asyncio.sleep(.1)
                            await asyncio.sleep(.1)
#s                    |   |   |   |
                        #0#1#2
#s                    |   |   |   |
                    print(color.yellow()+'\tcam conn_try', conn_try)
                    print(color.red()+'\tcam out\n}\n'+color.normal())
                    sys_info.setd('cam_server','timeout',conn_try)
                    s.close()
                    del s
                except OSError as e:
                    print('cam socket failed',str(e))
        gc.collect()
        await asyncio.sleep(.1)