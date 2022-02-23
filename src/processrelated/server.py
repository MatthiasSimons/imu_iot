from src.gateway import PNK

class Server():
    gw = PNK(collection = "training")
    gw.insert(training=True)