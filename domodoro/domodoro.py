from subprocess import check_output
import json
import sys
from time import time, sleep
import os

work_minutes = 25
break_minutes = 10
long_break_minutes = 20

status_path = '/tmp/domodoro.json'

def play_sound(sound_name):
  path = ''
  if not os.path.exists('./ping.mp3'):
    path = '../domodoro'
  extra_options = []
  if sound_name == 'coin.mp3':
    extra_options.append('--speed=0.4')
  elif sound_name == 'ping.mp3':
    extra_options.append('--volume=50')
  check_output(['mpv', f'{sys.path[0]}/{path}/{sound_name}'] + extra_options)

default_status = {
  'timer_timestamp': None,
  'type': 'off',
  'title': None,
}

def read_status():
  if not os.path.exists(status_path):
    write_status(default_status)
  status = None
  with open(status_path, 'r+') as f:
    status = f.read()
  if status.strip() == '':
    write_status(default_status)
  return json.loads(status)

def write_status(status):
  with open(status_path, 'w') as f:
    f.write(json.dumps(status))

def process_status(status):
  if status['type'] == 'off':
    write_status(default_status)
    return

  elapsed = time() - status['timer_timestamp']
  if elapsed > 0:
    check_output(['notify-send', '-t', '3000', f'Finished timer {status["title"]}'])
    if status['type'] == 'work':
      play_sound('coin.mp3')
      write_status(default_status)
    elif status['type'] == 'break':
      play_sound('ping.mp3')
      

def start_timer(duration, title='work'):
  type_map = {
    'timer':'work',
    'work':'work',
    'break':'break',
    'long break':'break',
  }
  print(f'starting timer of type {type_map[title]} titled {title}')
  status = dict(default_status)
  status['timer_timestamp'] = time() + duration * 60
  status['type'] = type_map[title]
  status['title'] = title
  with open(status_path, 'w') as f:
    f.write(json.dumps(status))

def quick_stop():
  status = read_status()
  if status['timer_timestamp'] == None:
    return False
  elapsed = time() - status['timer_timestamp']
  if elapsed > 0 and status['type'] == 'break':
    write_status(default_status)
    return True

  return False

def tick():
  status = read_status()
  process_status(status)
  return read_status()

if __name__ == '__main__':
  if quick_stop():
    quit()

  options = [
    ' work ',
    ' break ',
    ' long break ',
  ]
  if read_status()['type'] != 'off':
    options.insert(0, ' cancel ')
  print(options)
  options = '\n'.join(options)
  cmd = check_output(['dmenu', '-b', '-nb', '#000', '-sb', '#FF0', '-nf', '#FFF', '-sf', '#000'], text=True, input=options).strip()
  if cmd == 'work':
    start_timer(work_minutes, 'work')
  elif cmd == 'break':
    start_timer(break_minutes, 'break')
  elif cmd == 'long break':
    start_timer(long_break_minutes, 'long break')
  elif cmd == 'cancel':
    write_status(default_status)
  else:
    start_timer(int(cmd), 'timer')
