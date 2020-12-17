from structure import color, sys_info, urequests
import json

def check(module_name):
  global git_sys_info, esp_sys_info, git_url
  esp_sys_info=sys_info.esp_info()
  git_sys_info=sys_info.git_info()
  git_url=sys_info.git_url()
  print('\n'+color.blue()+'git_sys_info:',color.normal(), str(git_sys_info).replace(',',',\n').replace('{','{\n ').replace('}','\n}'))
  print('\n'+color.red()+'esp_sys_info:',color.normal(), str(esp_sys_info).replace(',',',\n').replace('{','{\n ').replace('}','\n}'))

  sys_state=(False, 'system', 'updated')
  try:
    if module_name == '':
      for module in git_sys_info:
        try:
          if esp_sys_info[module] != git_sys_info[module]:
            sys_state = (False, module, "outdated")
        except:
          print("error: module '"+ module +"' not founded")
      return sys_state
    else:
      if esp_sys_info[module_name] != git_sys_info[module_name]:
        return True, module_name, "outdated"
      else:
        return False, module_name, "updated"
  except:
    return "error: module '"+ module_name +"' not founded"


def system():
  update_list = []
  for module in git_sys_info:
    try:
      if esp_sys_info[module] != git_sys_info[module]:
        update_list.append(module)
    except:
      update_list.append(module)
      print("error: module '"+ module +"' not founded on local esp system")
  print('OUTDATED Modules:', update_list)
  for outdated_module in update_list:
    print(color.blue(),'\nUpdating:', outdated_module+color.normal())
    git_file(outdated_module)


def git_file(file_name):
  try:
    outdated_file=urequests.get(git_url+file_name)
    try:
      file = open("/structure/"+file_name,"w")
      file.write(outdated_file.text)
      file.close()
      print(color.normal()+outdated_file.text)
      print(color.green(),file_name,'updated\n'+color.normal())
    except:
      print("error: didn't found",file_name)
  except:
    print('error: getting git file')


def remote(file_name,file_dir,from_url):
  print(color.blue,'\nRemotely updating:',file_name,'from:', from_url ,'\n')  
  try:
    print('Get:',from_url)
    remote_file=urequests.get(from_url)
    print('Got:',from_url)
    try:
      file = open(file_dir+"/"+file_name,"w")
      file.write(remote_file.text)
      file.close()
      print(color.normal()+remote_file.text)
      print(color.green(),file_name,'updated\n'+color.normal())
      import machine
      machine.reset()
    except:
      print("error: didn't found",file_name)
  except:
    print('error: getting git file')
    

def read_remote(file_name,dir_url):
  print(color.blue()+'\nReading',file_name,'from',dir_url,'\n')
  try:
    remote_file=urequests.get(dir_url+file_name)
    print('got file\n', remote_file.text+color.normal())
    return remote_file
  except:
    print(color.red, 'error reading remote file'+color.normal())
    return 'error reading remote file'
  
