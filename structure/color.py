def red():
  return "\033[1;31;40m"


def green():
  return "\033[1;32;40m"


def yellow():
  return "\033[1;33;40m"


def blue():
  return "\033[1;34;40m"

def test():
    for var1 in range(1,2):
        for var2 in range(30,37):
            for var3 in range(40,47):
                print("\033["+str(var1)+";"+str(var2)+";"+str(var3)+"mASDASd"+str(var1)+";"+str(var2)+";"+str(var3))

def normal():
  return "\033[0;0;0m"
