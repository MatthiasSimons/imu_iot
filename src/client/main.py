from machine import I2C, Pin, Timer, RTC
from time import sleep_ms
from imu import MPU6050
import network
import usocket as socket
import time
import json

DataCounter = 0
port = 8000
BUFFER_SIZE = 1024
status = True
server_connection = False
accel_array = []
batch_size = 1

ssid, pwd, ip = "", "", '' # enter ssid, password and ip


def read_imu(tim):
    try:
        s.send("{};{}?".format(str(rtc.datetime()), str(accel.xyz)).encode())

    except Exception as e:
        status = False
        tim.deinit()
        # s.close()
        print("Error occured:", e)


i2c = machine.I2C(scl=Pin(5), sda=Pin(4), freq=100000)
mpu6050 = MPU6050(i2c)
accel = mpu6050.accel
rtc = machine.RTC()

#
# connecti WiFi
#

sta_if = network.WLAN(network.STA_IF)
visible_wifis = [w[0].decode("utf-8") for w in sta_if.scan()]
print("network", ssid)
if not sta_if.isconnected():
    print('connecting to network...')
    if ssid not in visible_wifis:
        print("ssid not found")
    sta_if.active(True)
    sta_if.connect(ssid, pwd)
    while not sta_if.isconnected():
        pass
print('network config:', sta_if.ifconfig())

print("connect to server")
# create socket
s = socket.socket()
addrinfos = socket.getaddrinfo(ip, port)

while not server_connection:
    try:
        s.connect(addrinfos[0][4])
        server_connection = True
        print("server connected")

    except Exception as e:
        print("error occured:", e)
        sleep_ms(2000)

tim = Timer(-1)
tim.init(period=25, mode=Timer.PERIODIC, callback=read_imu)

print("start measuring...")
while status:
    continue
print("stop measuring")

