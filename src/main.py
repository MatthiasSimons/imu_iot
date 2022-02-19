# # import multiprocessing as mp
# # import src.userrelated.frontend
# #
# # src.userrelated.frontend.Frontend()
# #from src.userrelated.backend import Backend
# from src.processrelated.server import Server
# #
# # pool = mp.Pool(mp.cpu_count())
# # print("number if processors", mp.cpu_count())
# # # process_server = Server()
# # # process_frontend = Frontend()
# # # process_backend = Backend()
#
# #mp.Process(target=Server)
#
# from multiprocessing import Process
#
# def func1():
#     for i in range(0,100):
#         print(1)
#
# def func2():
#     for i in range(0, 10):
#         print(2)
#
# if __name__ == '__main__':
#   p1 = Process(target=Server)
#   p2 = Process(target=Server)
#   p1.start()
#   p2.start()
#   p1.join()
#   p2.join()