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

json_command={}

async def start(to):
    global json_command
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
                        print('Error getting data addr info')
                else:
                    print('data_host not ready')
                    await asyncio.sleep(3)
            else:
                conn_try=0
                print(color.green()+'{\n\tCONNECTING TO PYCOM DATA'+color.normal())
                try:
                    s = socket.socket()
                    s.setblocking(False)
                    connected = False
                    while connected == False:
                        try:
                            s.connect(data_address)
                        except OSError as e:
                            if str(e) == "127":
                                connected = True
                                conn_try = 0
                            else:
                                conn_try = conn_try+1
                                if conn_try > to:
                                    print(color.red()+'\tDATA CONN F'+color.normal())
                                    conn_try = to
                                    break
                        await asyncio.sleep(.1)
                        pass
                    if conn_try != to:
                        print(color.green()+'\tconnected to data_address'+color.normal())
                        conn_try = 0
                        try:
                            print('\tsending esp_data')
                            while True:
                                try:
                                    data = json.dumps(machine_data.get())
                                    data = data.encode()
                                    while data:
                                        sent = s.send(data)
                                        data = data[sent:]
                                    conn_try = 0
                                    break
                                except OSError as e:
                                    #print(e)
                                    if conn_try > to:
                                        print(color.red()+'DATA SEND F'+color.normal())
                                        break
                                    conn_try = conn_try+1
                                    
                            if conn_try != to:
                                print('\treceiving server data')
                                while True:
                                    try:
                                        res = s.recv(256)
                                        await asyncio.sleep(.1)
                                        if str(res).find('command') != -1:
                                            print('\tserver data received: ')
                                            print(res)
                                            try:
                                                js_res = json.loads(res)
                                                machine_data.parse_data(js_res)
                                            except:
                                                print('failed to parse json')
                                            break
                                    except OSError as e:
                                        if conn_try > to:
                                            print(color.red()+'DATA RECV F'+color.normal())
                                            break
                                        conn_try = conn_try + 1
                                        #print('error receiving '+str(e))
                            s.close()
                        except OSError as e:
                            print('data com failed '+ str(e))
                    print(color.yellow()+'\tdata conn_try', conn_try)
                    print(color.red()+'\tesp_data out\n}\n'+color.normal())
                    sys_info.setd('data_server','timeout',conn_try)
                    s.close()
                    del s
                except OSError as e:
                    print('data socket failed',str(e))
        gc.collect()
        await asyncio.sleep(.1)