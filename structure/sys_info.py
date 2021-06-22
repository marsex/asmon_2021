from structure import urequests, color
import json

def esp_info():
    try:
        sys_file = open('/structure/sys_info','r')
        esp_sys_info = json.loads(sys_file.read())
        sys_file.close()
        print('\n'+color.red()+'esp_sys_info:',color.normal(), str(esp_sys_info).replace(',',',\n').replace('{','{\n ').replace('}','\n}'))
        return esp_sys_info
    except:
        print('\terror getting esp system info\n}\n')
        return False

def git_info():
    try:
        git_sys_info = json.loads(urequests.get(get('esp_sys_info')['git_url']+'sys_info').text)
        print('\n'+color.blue()+'git_sys_info:',color.normal(), str(git_sys_info).replace(',',',\n').replace('{','{\n ').replace('}','\n}'))
        return git_sys_info
    except:
        print('\terror getting git system info\n}\n')
        return False

def get(key):
    return state[key]

def set(key,value):
    print(key,value)
    try:
        state[key]=value
        return True
    except:
        return False
        
def setd(key,key2,value):
    print(key,key2,value)
    try:
        state[key][key2]=value
        return True
    except:
        return False

def save():
    return True

def restore():
    return False

def reset():
    global state
    state={
        'wifi':'',
        'cam':'',
        'data_server':{'host':'','port':'','address':'','timeout':''},
        'cam_server':{'host':'','port':'','address':'','timeout':''},
        'esp_sys_info':'',
        'git_sys_info':'',
        'server_list':'null'
    }
    set('esp_sys_info',esp_info())
    