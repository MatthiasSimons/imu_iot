# start server
from src.gateway import Gateway

if __name__ == "__main__":
    gw = Gateway()
    gw.connect_socket()
    conn = gw.listen_socket()
    gw.write(conn, insert=False)
