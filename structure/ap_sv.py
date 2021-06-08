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
    await asyncio.sleep(.18)
    print(color.yellow()+'STARTING AP_SV'+color.normal())
    await asyncio.sleep(1)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    a = ('0.0.0.0', 80)
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
            res = poller.poll(200)  # time in milliseconds
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

                if req[1] == 'app':
                    print('\taccesing', req[1])
                    html = hdr.get_index()
                    index_data = (b'%s' % html)
                    while True:
                        try:
                            while index_data:
                                sent = client.send(index_data)
                                index_data = index_data[sent:]
                            break
                        except OSError as e:
                            print(e)
                elif req[1] == 'gpio':
                    pin, value = req[2], req[3]
                    command_json = {'command': 'output_state', 'data': {'pin':pin,'value':value}}
                    machine_data.parse_data(command_json)

                    esp_data = machine_data.get()
                    gpio_output = esp_data['gpio']['output_state']

                    json_response = json.dumps({'command':'output_state','output_state': gpio_output})
                    json_header = hdr.get('json').replace('$len',str(len(json_response)))

                    client.send(b'%s' % json_header)
                    client.sendall(json_response.encode())
                elif req[1] == 'credentials':
                    ssid, psw = req[2], req[3]

                    wifi.set_credentials(ssid+','+psw)
                    json_response = json.dumps({'command':'credentials','state': 'saved'})
                    json_header = hdr.get('json').replace('$len',str(len(json_response)))

                    client.send(b'%s' % json_header)
                    client.sendall(json_response.encode())
            client.close()
            print(color.red()+ '\tConnection ' + ip + ':' + port + ' closed'+color.normal()+'\n}')
        except OSError as e:
            if str(e) != '[Errno 11] EAGAIN':
                print(e)
        await asyncio.sleep(.1)