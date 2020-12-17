from structure import machine_data, color, cam, wifi, async_sys
from structure import headers as hdr
from time import sleep
import camera
import uasyncio as asyncio
import socket
import uerrno
import gc
import uselect
import json

wifi.ap_on()
wifi.scan_networks()

cam.start()

data_host = "asmon.com.ar"
cam_host = "asmon.com.ar"
USER = "espcam"
data_address = ''
cam_address = ''
json_command={}

def start(to):
    global data_address, cam_address
    
    while data_address == '':
        try:
            data_address = socket.getaddrinfo(data_host, 8080)[0][-1]
            print('got data addr info')
        except:
            data_address = ''
            print('Error getting data addr info')
        sleep(.1)
        pass

    while cam_address == '':
        try:
            cam_address = socket.getaddrinfo(data_host, 8081)[0][-1]
            print('got cam addr inf o')
        except: 
            cam_address = ''
            print('Error getting cam addr info')
        sleep(.1)
        pass

    try:
        main_loop = asyncio.new_event_loop()  
        main_loop.create_task(data(to))
        main_loop.create_task(sendcam(to))
        main_loop.create_task(ap_cam(to))
        main_loop.create_task(ap_sv(to))
        main_loop.run_forever()
    except OSError as e:
        print("async failed"+str(e)) 

    print("async out")   
    gc.collect()
    gc.mem_free()
    
async def ap_sv(to):
    print(color.yellow()+'STARTING AP_SV'+color.normal())
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

                if req[1] == 'app':
                    print('\taccesing',req[1])
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

                    command_json = {'command': 'output_state', 'data': pin+'='+value}
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

async def ap_cam(to):
    print(color.yellow()+'STARTING AP_CAM'+color.normal())
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

async def data(to):
    global json_command
    print(color.green()+'STARTING PYCOM DATA'+color.normal())
    await asyncio.sleep(1)
    while True:
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
                                await asyncio.sleep(.2)
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
                                res = str(s.recv(256))
                                await asyncio.sleep(.1)
                                if res.find('command') != -1:
                                    print('\tserver data received: ')
                                    print('\t'+res)
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
            async_sys.set('data_server',{'addr':data_address,'timeout':conn_try})
            s.close()
            del s
        except OSError as e:
            print('data socket failed',str(e))
        gc.collect()
        await asyncio.sleep(.1)

async def sendcam(to):
    print(color.blue()+'STARTING PYCOM CAM'+color.normal())
    await asyncio.sleep(1)
    while True:
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
            async_sys.set('cam_server',{'addr':cam_address,'timeout':conn_try})
            s.close()
            del s
        except OSError as e:
            print('cam socket failed',str(e))
        
        gc.collect()
        await asyncio.sleep(.1)
