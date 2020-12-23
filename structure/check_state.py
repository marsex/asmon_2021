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

async def check_state(loop_delay):
    print(color.yellow()+'wifi state running'+color.normal())
    while True:
        cd_state, cd_ssid, cd_pw = wifi.get_credentials()

        st_wlan = network.WLAN(network.STA_IF)
        wifi_st = st_wlan.isconnected()
        
        server_list = sys_info.get('server_list')
        data_server = sys_info.get('data_server')
        cam_server = sys_info.get('cam_server')
        git_sys_info = sys_info.get('git_sys_info')
        
        sys_info.set('wifi',wifi_st)
        if wifi_st == False:
            if cd_state == True:
                print('Connecting to:',cd_ssid,cd_pw)
                st_wlan.active(True)
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