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
    await asyncio.sleep(.24)
    print(color.yellow()+'STARTING AP_CAM'+color.normal())
    await asyncio.sleep(1)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    a = ('0.0.0.0', 81)
    s.bind(a)
    s.listen(2)  # queue at most 2 clients
    s.setblocking(False)
    while True:
        try: 
            client, addr = s.accept()
            ip, port = str(addr[0]), str(addr[1])
            print('{')
            print(color.yellow()+'\tConnection from ' + ip + ':' + port)
            
            # Use:
            poller = uselect.poll()
            poller.register(client, uselect.POLLIN)
            res = poller.poll(50)  # time in milliseconds
            if not res:
                print('\toperation timed out')
            else:
                client_data = client.recv(1024)
                client_data = client_data.decode('utf-8')
                req = client_data.split(' ')
                try:
                    print('\t',req[0],'##', req[1],"##", addr)
                    req = req[1].split('/')
                    print('req split', req)
                except OSError as e:
                    print('\t#failed to split req', e)
                
                while True:
                    try:
                        if req[1] == 'live':
                            print('\taccesing',req[1])
                            client.send(b'%s' % hdr.get('stream'))
                            
                            client.send(b'%s' % hdr.get('frame'))
                            n_try = 0
                            buf = False
                            cam.light('1')
                            while (n_try < 10 and buf == False): #{
                                # wait for sensor to start and focus before capturing image
                                #print('\tgetting img')
                                buf = camera.capture()
                                if (buf == False): await asyncio.sleep(1)
                                n_try = n_try + 1
                            cam.light('0')
                            #print('\tsending img:', len(buf))
                            try:             
                                while buf:
                                    sent = client.send(buf)
                                    buf = buf[sent:]
                                #print('\timg sent')
                            except OSError as e:
                                print('send apcam error',e)
                            client.send(b'\r\n')  # send and flush the send buffer
                    except OSError as e:
                        print(e)
                        break
                    await asyncio.sleep(.1)
                    
            client.close()
            print(color.red()+ '\tConnection ' + ip + ':' + port + ' closed'+color.normal()+'\n}')
        except OSError as e:
            if str(e) != '[Errno 11] EAGAIN':
                print(e)
        await asyncio.sleep(.1)