import RPi.GPIO as GPIO
import time
import os
import glob

GPIO.setmode(GPIO.BCM)

TRIG_PIN = 23
ECHO_PIN = 24
IR_PIN   = 17

GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setup(IR_PIN, GPIO.IN)

# Setup for DS18B20
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temperature():
    """Reads the temperature from the DS18B20 sensor."""
    with open(device_file, 'r') as f:
        lines = f.readlines()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        with open(device_file, 'r') as f:
            lines = f.readlines()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
    return None

def read_ultrasonic_distance():
    """Reads the distance using the ultrasonic sensor."""
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()
    while GPIO.input(ECHO_PIN) == 1:
        stop_time = time.time()

    elapsed = stop_time - start_time
    distance = (elapsed * 34300) / 2
    return distance

def read_ir_sensor():
    """Checks if the infrared sensor is triggered."""
    return GPIO.input(IR_PIN) == 0

def cleanup():
    GPIO.cleanup()