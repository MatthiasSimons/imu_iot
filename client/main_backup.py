from machine import I2C, Pin, Timer
from time import sleep_ms
from imu import MPU6050
import wifi
#import mqtt

DataCounter = 0
accel_array = []

def read_imu(tim):
    global DataCounter
    global accel_array

    data_string = "{0:3.5f},{1:3.5f},{2:3.5f}\n".format(accel.x, accel.y, accel.z)
    accel_array.append(data_string)
    DataCounter += 1
    print(DataCounter)

i2c = machine.I2C(scl=Pin(5), sda=Pin(4), freq=100000)
mpu6050 = MPU6050(i2c)
accel = mpu6050.accel

tim = Timer(-1)
tim.init(period=500, mode=Timer.PERIODIC, callback=read_imu)

print('Start...')

while True:
    #print("while SChleife")
    if DataCounter>5:
        tim.deinit()
        break

data_file = open('imu.csv', 'w')
data_file.write('A_X,A_Y,A_Z\n')

for i in accel_array:
    data_file.write(i)

data_file.close()
print("Saved CSV-File")

print("Connect Wifi")

wifi.do_connect()

print("Wifi connected")

print("connect mqtt")


#### in read_imu einfügn
from umqtt.simple import MQTTClient
import network
import machine
import time
import utime

device_name, mqtt_server, mqtt_port = "SimonsMeyer", "192.168.0.102", 1883

client = MQTTClient(device_name, mqtt_server, mqtt_port)
mqttConnected=client.connect()
accel = mpu6050.accel
dt = machine.RTC().datetime()
s = '{ "device":"' + str(device_name) + '","Ax": ' + str(accel.x) + ',"Ay": ' + str(accel.y) + ',"Az": ' + str(accel.z) + ', "time":"' + str(dt) + '"}'
client.publish('IoT-PT/imudata/'+device_name, s)
client.disconnect()

