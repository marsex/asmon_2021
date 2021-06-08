import network
import socket
from time import sleep

scan_list = []

def ap_on():
    ap_wlan = network.WLAN(network.AP_IF)
    ap_wlan.active(True)
    ap_wlan.config(essid='ASMON AP System#2')
    ap_wlan.config(authmode=3, password='12551255')
    ap_localhost = ap_wlan.ifconfig()[0]  # get ip addr
    print('AP Configurated\n')
    return ap_localhost


def scan_networks():
    global scan_list
    station = network.WLAN(network.STA_IF)
    station.active(False)
    
    station.active(True)
    while True:
        try:
            #print('Scanning networks')
            scan_list = station.scan()
            if len(scan_list) != 0:
                print(scan_list)
                break
        except:
            print('scan failed')
        sleep(2)
    print('\n\nStopping Scan')


def get_networks():
    return scan_list


def get_credentials():
    file = open("credentials","r")
    data = file.read()
    file.close()
    cred_ssid=data.split(",")[0]
    cred_psw=data.split(",")[1]
    if cred_ssid == 'null':
        return False,'null','null'
    else:
        return True,cred_ssid,cred_psw


def set_credentials(c_data):
    print('Got credentials: ', c_data)
    print('Saving credentials...')
    file = open("credentials","w")
    file.write(c_data)
    file.close()
    print('Credentials Saved')


def connect(cred_ssid,cred_psw):
    print('\n{\n\tConnecting to network: ' +cred_ssid)
    st_wlan = network.WLAN(network.STA_IF)
    st_wlan.active(True)

    if cred_ssid != 'null':
        if not st_wlan.isconnected():
            st_wlan.connect(cred_ssid,cred_psw)
            while not st_wlan.isconnected():
                pass
            print('\tConnected, st_wlan:', st_wlan.ifconfig(), '\n}\n')
            return True
        else:
            print('\tAlready connected to:', cred_ssid, '\n\t', st_wlan.ifconfig(),'\n}\n')
            return True
    else:
        try:
            print('\n{\n\treconnecting to network: ' +cred_ssid)
            if not st_wlan.isconnected():
                st_wlan.connect()
                while not st_wlan.isconnected():
                    pass
                print('\tConnected, st_wlan:', st_wlan.ifconfig(), '\n}\n')
                return True
            else:
                print('\tAlready connected to:', st_wlan.ifconfig(), '\n}\n')
                return True
        except:
            print('failed to reconnect')
            print('get wifi credentials')
            return False