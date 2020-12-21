from structure import urequests
import json

def git_url():
  return git_sys_info['git_url']

def esp_info():
  print('\n{\n\tgetting esp system info')
  try:
    sys_file = open('/sys_info','r')
    esp_sys_info = json.loads(sys_file.read())
    sys_file.close()
    print('\tgot esp system info\n}')
    return esp_sys_info
  except:
    print('\terror getting esp system info\n}\n')
    return False


def git_info():
  print('\n{\n\tgetting git system info')
  try:
    git_sys_info = json.loads(urequests.get(esp_sys_info['git_url']+'sys_info').text)
    print('\tgot git system info\n}')
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
        'server_list':''
    }
    
esp_sys_info = esp_info()