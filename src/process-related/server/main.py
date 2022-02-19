from src.gateway import PNK

gw = PNK(collection = "process_data")
gw.insert(training=False)