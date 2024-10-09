import json
from datetime import datetime, date, timedelta
import time
from getpass import getuser
from socket import gethostname
import psutil
import re
from subprocess import check_output
import sys
sys.path.append(sys.path[0] + '/../domodoro')
import domodoro as domodoro_api

def exec(cmd):
  return check_output(cmd.split(' ')).decode()

def property(name, value):
  return '"{_name}":"{_value}"'.format(_name = name, _value = value)

def block(text, color = '#ffffff'):
  res = '{'
  res += property('full_text', text)+','+property('color', color)
  res += '}' 
  return res


def time(seconds = False):
  now = datetime.now()
  currentTime = now.strftime(' %-H:%M' + (':%S' if seconds else '') + '  ')
  return block(currentTime)

def othertime(seconds = False, offset = 0, title=''):
  now = datetime.now() - timedelta(hours=offset)
  currentTime = now.strftime('%-H:%M' + (':%S' if seconds else '') + '  ')
  return block(f'{title} {currentTime}', '#aaaaaa')

def longDate():
  now = datetime.now()
  currentDate = now.strftime('%A, %B %-d  (%d.%m.%-Y)')
  return block(currentDate, '#ea9635')

def user():
  name = getuser()
  host = gethostname()
  return block(name + ' ('+ host+')')

def mem():
  mem = psutil.virtual_memory()
  total = str(int((mem.total/100000000))/ 10)
  used =  str(int((mem.used/100000000)) / 10)
  percentage = mem.used/mem.total
  color = '#ffffff'
  if (percentage < 0.5):
    color = '#00ff00'
  elif (percentage < 0.8):
    color = '#ffffff'
  else:
    color = '#ff0000'
  return block('RAM ' + used + '/' + total + 'G', color)

def deadline():
  now = date.today()
  deadline = date(2029, 4, 6)
  difference = deadline - now
  return block(str(difference.days), '#ff0000')

def battery(batteryHealthMode=False):
  acpi = exec('acpi -b')
  if len(acpi) == 0:
    return block('')
  level = int(re.search(', (\d?\d?\d)%', acpi).group(1))
  color = '#00ff00'
  
  #batteryHealthMode keeps the battery level between 20% and 80%
  if (batteryHealthMode):
    if (level < 20 or level > 80):
      color = '#ff0000'
    elif (level < 30):
      color = '#ffaa00'
  else:
    if (level < 30):
      color = '#ff0000'
    elif (level < 60):
      color = '#ffaa00'
      
  width = 10
  lvl = int(level/100 * width) + 1
  bar = lvl*'#' + (width-lvl)*'-'
  out = str(level) + '%'+ ' ' + bar
  return block(out, color)

def domodoro():
  status = domodoro_api.tick()
  if (status['timer_timestamp'] == None) or (status['title'] == None) or (status['type'] == 'off'):
    return block('off', '#0000ff')
  title = status['title']
  elapsed = float(status['timer_timestamp']) - datetime.now().timestamp()
  if elapsed < 0:
    return block(f'{title} {int(elapsed/60) * -1} min ago', '#ffff00')
  return block(f'{title} {int(elapsed / 60)}:{int(elapsed % 60):>02}', '#ffff00')
  
blocks = [
  domodoro(),
#  user(), 
  mem(),
  battery(batteryHealthMode=False),
  longDate(),
  othertime(seconds=False, offset=12, title='west'),
  time(seconds=False), 
]

line = ',['
for i in range(len(blocks)):
  line += blocks[i] + ', '*(i != len(blocks)-1)
line += ']'
print(line)
