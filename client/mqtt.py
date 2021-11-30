from umqtt.simple
import MQTTClient
import network
import machine
import time
import utime

client = MQTTClient(device_name, mqtt_server, mqtt_port)
mqttConnected=client.connect()
accel = mpu6050.accel
dt = machine.RTC().datetime()
s = '{ "device":"' + str(device_name) +\ '","Ax": ' + str(accel.x) + \ ',"Ay": ' + str(accel.y) + \ ',"Az": ' + str(accel.z) + \ ', "time":"' + str(dt) + '"}' c
lient.publish('IoT-PT/imudata', s)
client.disconnect()