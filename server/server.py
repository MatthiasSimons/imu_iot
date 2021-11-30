import socket
TCP_IP = '192.168.0.112'
TCP_PORT = 8000
BUFFER_SIZE = 20480
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
print("Waiting for Connection...")
s.listen(1)
data_string = []
conn, addr = s.accept()
print('Connection address:', addr)
while 1:
    data = conn.recv(BUFFER_SIZE)
    if not data:
        break
    data_string.append(data.decode())
    print(data_string)
conn.close()

def concDataSet(data_string):
    ax = []
    ay = []
    az = []
    for chunk in data_string:
        data_set = chunk.split('\n')
        # print(data_set)
        for nr_data in data_set:
            all_data = nr_data.split(',')
            # print(all_data)
            lengthdata = len(all_data)
            if lengthdata > 0:
                if len(all_data[0]) > 1:
                    ax.append(float(all_data[0]))
            if lengthdata > 1:
                if len(all_data[1]) > 1:
                    ay.append(float(all_data[1]))
            if lengthdata > 2:
                if len(all_data[2]) > 1:
                    az.append(float(all_data[2]))
    return ax, ay, az