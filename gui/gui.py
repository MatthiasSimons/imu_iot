import tkinter as tk
from tkinter import ttk

from tkinter import *

# these two imports are important
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
import threading

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Example")
        self.geometry('300x300')

        self.notebook = ttk.Notebook(self)

        self.Frame1 = Frame1()
        self.Frame2 = Frame2()

        self.notebook.add(self.Frame1, text='Monitoring')
        self.notebook.add(self.Frame2, text='Training')

        self.notebook.pack()

class Tab(ttk.Frame):
    def __init__(self, container):
        super().__init__()

    def entry(self, text, row, column):
        self.label = ttk.Label(self, text=text)
        self.label.grid(column=column, row=row)
        self.entry = ttk.Entry(self)
        self.entry.grid(column=column+1, row=row, sticky=tk.E)

class Frame1(Tab):
    def __init__(self):
        super().__init__()
        self.entry(self, "asd", 1, 1)


class Frame2(Tab):
    def __init__(self):
        super().__init__()




if __name__ == '__main__':
    app = MainApplication()
    app.mainloop()