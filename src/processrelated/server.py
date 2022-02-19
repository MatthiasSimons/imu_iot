from src.gateway import PNK

class Server():
    gw = PNK(collection = "process_data")
    gw.insert(training=False)