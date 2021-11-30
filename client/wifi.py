import network
import ntptime
import machine

def settime():
    tm = (2021, 11, 23, 0, 10, 10, 0, 0)
    machine.RTC().datetime(tm)

def do_connect(ssid = "IoT_Robotic", pwd = "FH_AC4242424"):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to ' + ssid)
        wlan.connect(ssid, pwd)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    settime()
    print('current time=%s' % (machine.RTC().datetime(),))