import socket
tcp_ip = '192.168.1.1'

def listen(tcp_port = 80):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((tcp_ip, tcp_port))
    print("Waiting for Connection...")
    s.listen(1)
    conn, addr = s.accept()
    print('Connection address:', addr)
    return conn

for port in range(1,65535):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex((tcp_ip, port))
    if result == 0:
        print("Port {} is open".format(port))
        try:
            s.bind((tcp_ip, port))
            listen(tcp_port=port)
        except Exception as e:
            print(e)
            pass
    s.close()

#listen(tcp_port=64715)