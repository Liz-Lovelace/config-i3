#this script needs sudo priveleges to run!

from subprocess import Popen, PIPE, STDOUT
import json

def exec(cmd, sin = ''):
  cmd = cmd.split(' ')
  p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
  out = p.communicate(input=sin.encode('ascii'))
  return out[0].decode();

allDevices = json.loads(exec('lsblk -J'))
options = 'umount\n'
for dev in allDevices['blockdevices']:
  if ('children' in dev):
    for part in dev['children']:
      options += '| ' + part['name'] +' '+ part['size'] + '\n'

pick = exec('dmenu -b -nb #000 -sb #0F0 -nf #FFF -sf #000', options)

if ((pick == '') | (pick == '\n')):
  quit()

if (pick == 'umount\n'):
  #TODO: add umount capability
  print(exec('sudo umount /mnt'))
  quit()

if (pick[0] == '|'):
  pick = pick[2:].split(' ')[0]

print(exec('sudo mount /dev/'+pick+' /mnt'))