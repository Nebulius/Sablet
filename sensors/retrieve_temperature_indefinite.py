import os
import subprocess
import time

from path import Path

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = Path('/sys/bus/w1/devices/')
write_dir = Path('/home/pi/temp/')


def read_temp_raw(device_file):
    catdata = subprocess.Popen(['cat', device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = catdata.communicate()
    out_decode = out.decode('utf-8')
    lines = out_decode.split('\n')
    return lines


def read_temp(device_file):
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(device_file)

    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c


while True:
    for device_folder in base_dir.dirs('28*'):
        temp = read_temp(device_folder / 'w1_slave')
        write_file = write_dir / device_folder.basename()

        write_file.write_lines(str(time.time()) + '\t' + temp, append=True)
    time.sleep(1)
