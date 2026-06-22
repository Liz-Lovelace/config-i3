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

def block(text, color = '#000000'):
  res = '{'
  res += property('full_text', text)+','+property('color', color)
  res += '}' 
  return res

def time(seconds = False):
  now = datetime.now()
  currentTime = now.strftime(' %-H:%M' + (':%S' if seconds else '') + ' ')
  return block(currentTime)

def othertime(seconds = False, offset = 0, title=''):
  now = datetime.now() - timedelta(hours=offset)
  currentTime = now.strftime('%-H:%M' + (':%S' if seconds else ''))
  return block(f' {title} {currentTime} ', '#23292f')

def longDate():
  now = datetime.now()
  currentDate = now.strftime('%A, %B %-d  (%-Y-%m-%d)')
  return block(currentDate, '#23292f')

def user():
  name = getuser()
  host = gethostname()
  return block(name + ' ('+ host+')')

def temp():
  temp = open('/sys/class/thermal/thermal_zone0/temp', 'r').read()
  temp = int(temp) / 1000
  color = '#ffffff'
  if (temp > 70):
    color = '#d11149'
  elif (temp > 60):
    color = '#b5820a'
  elif (temp > 50):
    color = '#23292f'
  else:
    color = '#1a8a3f'
  return block(str(temp) + 'C', color)

def mem():
  mem = psutil.virtual_memory()
  total = str(int((mem.total/100000000))/ 10)
  used =  str(int((mem.used/100000000)) / 10)
  percentage = mem.used/mem.total
  color = '#23292f'
  if (percentage < 0.5):
    color = '#1a8a3f'
  elif (percentage < 0.8):
    color = '#23292f'
  else:
    color = '#d11149'
  return block('RAM ' + used + '/' + total + 'G', color)

def battery(batteryHealthMode=False):
  acpi = exec('acpi -b')
  acpi_entries = acpi.split('\n')
  if len(acpi_entries[0]) == 0:
    acpi = acpi_entries[1]
  else:
    acpi = acpi_entries[0]

  if len(acpi) == 0:
    return block('battery not found')

  level = int(re.search(', (\d?\d?\d)%', acpi).group(1))

  if level == 0:
    acpi = acpi_entries[1]
    level = int(re.search(', (\d?\d?\d)%', acpi).group(1))

  color = '#1a8a3f'
  
  #batteryHealthMode keeps the battery level between 20% and 80%
  if (batteryHealthMode):
    if (level < 20 or level > 80):
      color = '#ff2e6e'
    elif (level < 30):
      color = '#e8a317'
  else:
    if (level < 30):
      color = '#ff2e6e'
    elif (level < 60):
      color = '#e8a317'
      
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
  #domodoro(),
#  user(), 
  temp(),
  mem(),
  battery(batteryHealthMode=False),
  othertime(seconds=False, offset=12, title='us-west'),
  othertime(seconds=False, offset=9, title='us-east'),
  othertime(seconds=False, offset=5, title='utc'),
  othertime(seconds=False, offset=2, title='moscow'),
  time(seconds=False), 
  longDate(),
]

line = ',['
for i in range(len(blocks)):
  line += blocks[i] + ', '*(i != len(blocks)-1)
line += ']'
print(line)
