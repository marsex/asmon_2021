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
    machine.reset()

async def check_state(loop_delay):
    print(color.yellow()+'wifi state running'+color.normal())
    while True:
        cd_state, cd_ssid, cd_pw = wifi.get_credentials()

        st_wlan = network.WLAN(network.STA_IF)
        st_wlan.active(True)
        
        wifi_st = st_wlan.isconnected()
        server_list = sys_info.get('server_list')
        data_server = sys_info.get('data_server')
        cam_server = sys_info.get('cam_server')
        git_sys_info = sys_info.get('git_sys_info')
        sys_info.set('wifi',wifi_st)
        if wifi_st == False:
            if cd_state == True:
                print('Connecting to:',cd_ssid,cd_pw)
                st_wlan.connect(cd_ssid,cd_pw)
            else:
                print('Waiting for Wifi Credentials')
        else:
            if git_sys_info == '':
                sys_info.set('git_sys_info',sys_info.git_info())
                if update.check('sys_info')[0] == True:
                    print('\nSystem OUTDATED')
                    update.system()
                    print('\nSystem UPDATED')
                    print('\nRestarting system\n-----------------------\n\n')
                    machine.reset()
                else:
                    print('\nSystem updated\nStart system')
                
            if server_list == '':
                try:
                    server_request = update.read_remote('server_list',sys_info.get('esp_sys_info')['git_url'])
                    server_list = json.loads(server_request.text)
                    data_host, data_port = server_list['data_host'][0].split(':')
                    cam_host, cam_port = server_list['cam_host'][0].split(':')
                    
                    sys_info.set('server_list',server_list)
                    sys_info.setd('data_server','host',data_host)
                    sys_info.setd('data_server','port',data_port)
                    sys_info.setd('cam_server','host',cam_host)
                    sys_info.setd('cam_server','port',cam_port)
                except:
                    sys_info.reset()

        await asyncio.sleep(loop_delay)

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
                    sys_info.setd('data_server','timeout',conn_try)
                    s.close()
                    del s
                except OSError as e:
                    print('data socket failed',str(e))
        gc.collect()
        await asyncio.sleep(.1)

async def sendcam(to):
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

start(50)