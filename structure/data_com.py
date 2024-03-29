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
    await asyncio.sleep(.6)
    print(color.green()+'STARTING PYCOM DATA'+color.normal())
    await asyncio.sleep(1)
    while True:
        data_server = sys_info.get('data_server')
        data_host = data_server['host']
        port = data_server['port']
        data_address = data_server['address']
        wifi_st = sys_info.get('wifi')
        if wifi_st == False:
            await asyncio.sleep(3)
        if wifi_st != False:
            if data_address == '':
                if data_host != '':
                    try:
                        data_address = socket.getaddrinfo(data_host, port)[0][-1]
                        sys_info.setd('data_server','address',data_address)
                    except: 
                        data_address = ''
                        print('Error getting DATA addr info')
                else:
                    print('data_host not ready')
                    await asyncio.sleep(3)
            else:
                conn_try= 0
                timeout=0
                timeout_time=to
                trycount=0
                trycount_timeout=to
                print(color.green()+'{\n\tCONNECTING TO PYCOM DATA'+color.normal())
                try:
                    client = socket.socket()
                    client.setblocking(False)
                    connected = False
                    while connected == False:
                        try:
                            client.connect(data_address)
                        except OSError as e:
                            if str(e) == "127":
                                connected = True
                            else:
                                conn_try = conn_try+1
                                if conn_try > to:
                                    print(color.red()+'\tDATA CONN F'+color.normal())
                                    conn_try = to
                                    break
                        await asyncio.sleep(.1)
                        pass
                    #connected
                    if connected == True:
                        print(color.green()+'\tconnected to data_address'+color.normal())
                        while True:
                            if timeout > timeout_time:
                                print('failed to send data', timeout)
                                break
                            if trycount > trycount_timeout:
                                print('couldnt send data')
                                break
                            await asyncio.sleep(.1)

                            data = json.dumps(machine_data.get())
                            data = data.encode()
                            while True:
                                try:
                                    while data:
                                        sent = client.send(data)
                                        data = data[sent:]
                                    print(color.yellow(),'data sent',color.normal())
                                    machine_data.set('command',{'command':'wait'})
                                    timeout = 0
                                    break
                                except:
                                    timeout = timeout + 1

                            if timeout == 0:
                                while True:
                                    trycount = trycount + 1
                                    if trycount > trycount_timeout:
                                        print(color.yellow(),'couldnt receive data',color.normal())
                                        break
                                    print(color.yellow(),'tries to read:',trycount,timeout,color.normal())
                                    await asyncio.sleep(.1)
                                    try:
                                        res = client.recv(256)
                                        if str(res).find('command') != -1:
                                            print(color.yellow(),res,color.normal())
                                            timeout = 0
                                            break
                                    except:
                                        timeout = timeout +1
                                        if timeout > timeout_time:
                                            print(color.yellow(),'failed to read data',timeout,color.normal())
                                            break
                            if timeout == 0:
                                trycount = 0
                                try:
                                    js_res = json.loads(res)
                                except:
                                    print('failed to load json')
                                try:
                                    machine_data.parse_data(js_res)
                                except:
                                    print('failed to parse data',js_res)
                            
                    print(color.yellow()+'\tdata trycount', trycount)
                    print(color.red()+'\tdata out\n}\n'+color.normal())
                    sys_info.setd('data_server','timeout',conn_try)
                    client.close()
                    del client
                except OSError as e:
                    print('data socket failed',str(e))
        gc.collect()
        await asyncio.sleep(.1)