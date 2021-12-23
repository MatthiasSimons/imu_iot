from machine import I2C, Pin, Timer, RTC
from time import sleep_ms
from imu import MPU6050
import network
import usocket as socket
import time
import json

DataCounter = 0

#ssid, pwd, ip = "iPhone von Matthias", "Matthias", ""
#ssid, pwd, ip = "Tyrion LANnister", "ALM_PtrStr13", "192.168.0.129"
#ssid, pwd, ip = "Hoehlenstrahlung", "liebstdudiehoehle", '192.168.0.106'
#ssid, pwd, ip = "HI-EG-2-4", "778328778328778328", "192.168.178.21"
ssid, pwd, ip = "Haus LANnister", "JTzvt3hn5daw", "192.168.0.129"

status = True
server_connection = False

def read_imu(tim):
    global DataCounter
    global accel_array
    global rtc
    global status
    
    try:
        dt = rtc.datetime()
        year, month, day, weekday, hour, minute, second, microsecond = dt[0], dt[1], dt[2], dt[3], dt[4], dt[5], dt[6], dt[7]

        dt = "{}/{}/{} {}:{}:{}:{},".format(year, month, day, hour, minute, second, int(microsecond/10*10)) #prüfen
        data = "{0:3.5f},{1:3.5f},{2:3.5f}?".format(accel.x, accel.y, accel.z)

        data_string = dt+data
        #accel_array.append(data_string)
        
        DataCounter += 1

        s.send(data_string.encode())
        print(DataCounter, data_string)
    
    except Exception as e:
        status = False
        tim.deinit()
        s.close()
        print("Error occured:", e)
        
    


def do_connect(ssid, pwd):
    import network
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

i2c = machine.I2C(scl=Pin(5), sda=Pin(4), freq=100000)
mpu6050 = MPU6050(i2c)
accel = mpu6050.accel
rtc = machine.RTC()

######
# connecti WiFi

do_connect(ssid, pwd)


print("connect to server")

while not server_connection:
    try:
        # create socket
        BUFFER_SIZE = 1024
        s = socket.socket()

        # The server's hostname or IP address
        port = 8000
        
        addrinfos = socket.getaddrinfo(ip, port)
        s.connect(addrinfos[0][4])
        server_connection = True
        print("server connected")
    except Exception as e:
        print("error occured:", e)
        sleep_ms(2000)
        
        
     
tim = Timer(-1)
tim.init(period=500, mode=Timer.PERIODIC, callback=read_imu)
    
while status:
    pass
    #if DataCounter>=2:
    #    tim.deinit()
    #    s.close()
    #    print("measurement done")
    #    break

