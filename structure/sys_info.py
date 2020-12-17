from structure import urequests
import json

def git_url():
  return git_sys_info['git_url']

def esp_info():
  print('\n{\n\tgetting esp system info')
  global esp_sys_info
  try:
    sys_file = open('/structure/sys_info','r')
    esp_sys_info = json.loads(sys_file.read())
    sys_file.close()
    print('\tgot esp system info\n}')
    return esp_sys_info
  except:
    print('\terror getting esp system info\n}\n')


def git_info():
  print('\n{\n\tgetting git system info')
  global git_sys_info
  try:
    git_sys_info = json.loads(urequests.get(esp_sys_info['git_url']+'sys_info').text)
    print('\tgot git system info\n}')
    return git_sys_info
  except:
    print('\terror getting git system info\n}\n')

