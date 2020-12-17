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