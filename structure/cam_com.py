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
                conn_try= 0
                timeout=0
                timeout_time=to
                trycount=0
                trycount_timeout=to
                print(color.blue()+'{\n\tCONNECTING TO PYCOM CAM'+color.normal())
                try:
                    client = socket.socket()
                    client.setblocking(False)
                    connected = False
                    while connected == False:
                        try:
                            client.connect(cam_address)
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
                    if connected == True:
                        print(color.blue()+'\tconnected to cam_address'+color.normal())
                        while True:
                            if timeout > timeout_time:
                                print(color.blue(),'failed to send image',trycount,timeout,color.normal())
                                break
                            if trycount > trycount_timeout:
                                print('couldnt send image')
                                break
                            await asyncio.sleep(.1)
                            
                            img_data = {'user':machine_data.get_key('user'),'id':machine_data.get_key('id')}
                            id_data = json.dumps(img_data)
                            id_data = id_data.encode()
                            data = json.dumps({'command':'imgsent'})
                            data = data.encode()

                            frame = False
                            cam.light('1')
                            frame = camera.capture()
                            cam.light('0')
                            
                            frame = id_data + frame + data
                            while True:
                                try:
                                    while frame:
                                        sent = client.send(frame)
                                        frame = frame[sent:]
                                    print(color.blue(),'image sent',color.normal())
                                    timeout = 0
                                    break
                                except:
                                    timeout = timeout + 1
                                    if timeout > timeout_time*2:
                                        print(color.blue(),'failed to send image',trycount,timeout,color.normal())
                                        break
                            if timeout == 0:
                                while True:
                                    trycount = trycount + 1
                                    if trycount > trycount_timeout:
                                        print(color.blue(),'couldnt receive image data',color.normal())
                                        break
                                    print(color.blue(),'tries to read:',trycount,timeout,color.normal())
                                    await asyncio.sleep(.1)
                                    try:
                                        res = client.recv(256)
                                        if str(res).find('command') != -1:
                                            print(color.blue(),res,color.normal())
                                            timeout = 0
                                            break
                                    except:
                                        timeout = timeout +1
                                        if timeout > timeout_time:
                                            print(color.blue(),'failed to read image data',timeout,color.normal())
                                            break
                            if timeout == 0:
                                trycount = 0
                            print('') #send again
                    print(color.blue()+'\tcam trycount', trycount)
                    print(color.red()+'\tcam out\n}\n'+color.normal())
                    sys_info.setd('cam_server','timeout',conn_try)
                    client.close()
                    del client
                except OSError as e:
                    print('cam socket failed',str(e))
        gc.collect()
        await asyncio.sleep(.1)