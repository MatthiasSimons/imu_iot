from tkinter import ttk
from datetime import datetime
import pandas as pd
from tkinter import *
from matplotlib.dates import SecondLocator, DateFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
import threading
from src import gateway

class TrainingTab:
    def __init__(self, root):
        self.root = root
        self.database = gateway.BNK(collection="labels")

        self.continueInserting = False
        self.waschprogramme = {
            0: "Default",
            1: "Pflegeleicht 30",
            2: "Pflegeleicht 40",
            3: "Pflegeleicht 60",
            4: "Koch/Buntwäsche 30",
            5: "Koch/Buntwäsche 40",
            6: "Koch/Buntwäsche 60",
            7: "Koch/Buntwäsche 60 Flecken",
            8: "Koch/Buntwäsche 90",
            9: "Quickmix 30",
            10: "Schleudern",
            11: "Abpumpen",
            12: "Wolle 30",
            13: "Wolle kalt",
            14: "Fein 30", }

        self.waschprogramm = StringVar()
        self.gewicht = DoubleVar()
        self.drehzahl = StringVar()
        self.trommel = IntVar()
        self.pumpe = IntVar()
        self.betriebszustand = IntVar()

        self.waschprogramm.set("Default")
        self.gewicht.set(0.)
        self.drehzahl.set(0.)
        self.trommel.set(0)  # stillstand:0, rotieren:1, schleudern:1
        self.pumpe.set(0)
        self.betriebszustand.set(0)  # 0:bereit/fertig, 1:waschen, 2:spülen, 3:schleudern

        MainFrame = Frame(self.root, bg="White")
        MainFrame.grid()

        self.LeftFrame = Frame(MainFrame, bg="white")
        self.LeftFrame.pack(side=LEFT)
        self.RightFrame = Frame(MainFrame, bg="white")
        self.RightFrame.pack(side=RIGHT)

        TrainingTabPlot(root=self.LeftFrame)

        Label(self.RightFrame, text="Waschprogramm:", font=("Helvetica", "14", "bold", "underline")).grid(column=2, row=1)

        dropdown = OptionMenu(self.RightFrame, self.waschprogramm, *self.waschprogramme.values())
        dropdown.config(width=15)
        dropdown.grid(column=3, row=1, columnspan=2)

        ## row 2
        self.entry("Gewicht in (kg):", column=2, row=2, variable=self.gewicht)

        ## row 3
        self.entry("Drehzahl:", column=2, row=3, variable=self.drehzahl)

        ## row 4
        Label(self.RightFrame, text="Vorgang", font=("Helvetica", "14", "bold", "underline")).grid(column=2, row=4)
        Label(self.RightFrame, text="Betriebszustand", font=("Helvetica", "14", "bold", "underline")).grid(column=4, row=4)

        ## row 5
        Radiobutton(self.RightFrame, text="Bereit/Fertig", variable=self.betriebszustand, value=0).grid(column=4, row=5, sticky="w")
        Checkbutton(self.RightFrame, text="Pumpe", variable=self.pumpe).grid(column=2, row=5, sticky="w")

        ## row 6
        Radiobutton(self.RightFrame, text="Stillstand", variable=self.trommel, value=0).grid(column=2, row=6, sticky="w")
        Radiobutton(self.RightFrame, text="Waschen", variable=self.betriebszustand, value=1).grid(column=4, row=6, sticky="w")

        ## row 7
        Radiobutton(self.RightFrame, text="Rotieren", variable=self.trommel, value=1).grid(column=2, row=7, sticky="w")
        Radiobutton(self.RightFrame, text="Spülen", variable=self.betriebszustand, value=2).grid(column=4, row=7, sticky="w")

        ## row 8
        Radiobutton(self.RightFrame, text="Schleudern", variable=self.trommel, value=2).grid(column=2, row=8, sticky="w")
        Radiobutton(self.RightFrame, text="Schleudern", variable=self.betriebszustand, value=3).grid(column=4, row=8, sticky="w")

        Button(self.RightFrame, text="Start/Stop", command=self.gui_inserting_handler, bg="red", fg="black").grid(column=2, row=10, columnspan=4)

    def entry(self, text, column, row, variable=None):
        label = Label(self.RightFrame, text=text, font=("Helvetica", "14", "bold", "underline"))
        label.grid(column=column, row=row, sticky="w")

        entry = Entry(self.RightFrame, width=4, textvariable=variable)
        entry.grid(column=column+1, row=row, sticky="w")

    def change_inserting_state(self):
        if self.continueInserting == True:
            self.continueInserting = False
        else:
            self.continueInserting = True

    def inserter(self):
        i=0

        while self.continueInserting:
            parameters = {
                "Timestamp": datetime.now().strftime('%Y/%m/%d %H:%M:%S:%f'),
                "Waschprogramm": self.waschprogramm.get(),
                "Gewicht": self.gewicht.get(),
                "Drehzahl": self.drehzahl.get(),
                "Trommel": self.trommel.get(),
                "Pumpe": self.pumpe.get(),
                "Betriebszustand": self.betriebszustand.get(),
            }
            self.database.insert(parameters)
            print(i, parameters)
            i += 1

    def gui_inserting_handler(self):
        self.change_inserting_state()
        threading.Thread(target=self.inserter).start()

class TrainingTabPlot:
    def __init__(self, root):
        self.root = root
        self.database = gateway.BNK(collection="backend")

        self.continuePlotting = True

        self.fig = Figure()

        self.ax1 = self.fig.add_subplot(211)
        # self.ax1.set_title("Acceleration")
        # self.ax1.set_xlabel("time")
        # self.ax1.set_ylabel("Acceleration in (g)")
        # self.ax1.grid()
        self.ax1.plot([], [], marker='o', color='orange')

        self.ax2 = self.fig.add_subplot(212)
        # self.ax2.set_title("Fourier")
        # self.ax2.set_xlabel("Frequency in (Hz)")
        # self.ax2.set_ylabel("FFT(T)")
        # self.ax2.grid()
        self.ax2.plot([], [], marker='o', color='orange')

        self.fig.set_tight_layout(True)

        self.graph = FigureCanvasTkAgg(self.fig, master=self.root)
        self.graph.get_tk_widget().grid(column=1, row=2)

        threading.Thread(target=self.plotter()).start()
        self.root.update()

    def plotter(self):
        query = self.database.query(last=1)[0]

        acceleration = pd.DataFrame.from_dict(query["acceleration"], orient="index")
        acceleration.index = pd.to_datetime(acceleration.index, format="%Y/%m/%d %H:%M:%S:%f")
        acceleration.sort_index(inplace=True)
        x,y = acceleration.index, acceleration[0]

        acceleration_fft = query["acceleration_fft"]

        self.ax1.clear()
        self.ax2.clear()

        self.ax1.plot(x, y, marker='', color='orange')
        self.ax1.set_title("Acceleration")
        self.ax1.set_xlabel("time")
        self.ax1.set_ylabel("Acceleration in (g)")
        self.ax1.grid()
        self.ax1.xaxis.set_major_locator(SecondLocator(interval=1))
        self.ax1.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))

        self.ax2.plot(acceleration_fft, marker='', color='orange')
        self.ax2.set_title("Fourier")
        self.ax2.set_xlabel("Frequency in (Hz)")
        self.ax2.set_ylabel("FFT(T)")
        self.ax2.grid()
        self.graph.draw()

        keep_predicting = self.root.after(1000, self.plotter)

    def change_plotting_state(self):
        if self.continuePlotting == True:
            self.continuePlotting = False
        else:
            self.continuePlotting = True

    def gui_plotting_handler(self):
        #self.change_plotting_state()
        threading.Thread(target=self.plotter).start()

class MonitoringTabPlot:
    def __init__(self, root):
        self.root = root
        self.database = gateway.BNK(collection="backend")

        self.continuePlotting = True

        fig = Figure()

        self.ax3 = fig.add_subplot(311)
        self.ax3.plot([], [], marker='', color='orange')


        self.ax4 = fig.add_subplot(312)
        self.ax4.plot([], [], marker='', color='orange')

        self.ax5 = fig.add_subplot(313)
        self.ax5.plot([], [], marker='', color='orange')

        fig.set_tight_layout(True)

        self.graph = FigureCanvasTkAgg(fig, master=self.root)
        self.graph.get_tk_widget().grid(column=1, row=2)

        threading.Thread(target=self.plotter()).start()
        self.root.update()

    def plotter(self):
        query = self.database.query(last=1)[0]

        timestamp_history = query["timestamp_history"]
        prediction_history_trommel = query["prediction_history_trommel"]
        prediction_history_pumpe = query["prediction_history_pumpe"]
        prediction_history_betriebszustand = query["prediction_history_betriebszustand"]

        self.ax3.clear()
        self.ax4.clear()
        self.ax5.clear()


        self.ax3.plot(prediction_history_trommel, marker='', color='orange')
        self.ax3.set_title("Trommel")
        #self.ax3.set_xlabel("time")
        self.ax3.set_ylabel("state")
        self.ax3.grid()
        self.ax3.axes.xaxis.set_ticklabels([])
        #self.ax3.legend(labels=["1: Stillstand\n2: Rotieren\n3: Schleudern"])
        self.ax3.legend(labels=["1: Stillstand, 2: Rotieren, 3: Schleudern"],
                        loc='upper center', bbox_to_anchor=(0.5, -0.05),
                        fancybox=True, shadow=True, ncol=5)

        self.ax4.plot(prediction_history_pumpe, marker='', color='orange')
        self.ax4.set_title("Pumpe")
        self.ax4.set_xlabel("time")
        self.ax4.set_ylabel("state")
        self.ax4.grid()
        self.ax4.axes.xaxis.set_ticklabels([])
        #self.ax4.legend(labels=["1: An\n2: Aus\n"])
        self.ax4.legend(labels=["1: An, 2: Aus"],
                        loc='upper center', bbox_to_anchor=(0.5, -0.05),
                        fancybox=True, shadow=True, ncol=5)

        self.ax5.plot(prediction_history_betriebszustand, marker='', color='orange')
        self.ax5.set_title("Betriebszustand")
        self.ax5.set_xlabel("time")
        self.ax5.set_ylabel("state")
        self.ax5.grid()
        self.ax5.axes.xaxis.set_ticklabels([])
        self.ax5.legend(labels=["1: Bereit/Fertig, 2: Waschen, 3: Spülen, 4: Schleudern"],
                        loc='upper center', bbox_to_anchor=(0.5, -0.05),
                        fancybox=True, shadow=True, ncol=5)

        self.graph.draw()

        keep_predicting = self.root.after(1000, self.plotter)

    def change_plotting_state(self):
        if self.continuePlotting == True:
            self.continuePlotting = False
        else:
            self.continuePlotting = True

    def gui_plotting_handler(self):
        #self.change_plotting_state()
        threading.Thread(target=self.plotter).start()

class MonitoringTab:
  def __init__(self, root):
    self.root = root
    self.database = gateway.BNK(collection="backend")

    self.trommel_0 = DoubleVar()
    self.trommel_1 = DoubleVar()
    self.trommel_2 = DoubleVar()

    self.betriebszustand_0 = DoubleVar()
    self.betriebszustand_1 = DoubleVar()
    self.betriebszustand_2 = DoubleVar()
    self.betriebszustand_3 = DoubleVar()

    self.pumpe_0 = DoubleVar()
    self.pumpe_1 = DoubleVar()

    self.trommel_0.set(0.)
    self.trommel_1.set(0.)
    self.trommel_2.set(0.)

    self.betriebszustand_0.set(0.)
    self.betriebszustand_1.set(0.)
    self.betriebszustand_2.set(0.)
    self.betriebszustand_3.set(0.)

    self.pumpe_0.set(0.)
    self.pumpe_1.set(0.)

    MainFrame = Frame(self.root, bg="White")
    MainFrame.grid()

    self.LeftFrame = Frame(MainFrame)
    self.LeftFrame.pack(side=LEFT)
    self.RightFrame = Frame(MainFrame)
    self.RightFrame.pack(side=RIGHT)

    MonitoringTabPlot(root=self.LeftFrame)

    ## row 4
    Label(self.RightFrame, text="Vorgang", font=("Helvetica", "14", "bold", "underline")).grid(column=2, row=4)
    Label(self.RightFrame, text="Betriebszustand", font=("Helvetica", "14", "bold", "underline")).grid(column=4, row=4)

    ## row 5
    #Radiobutton(self.RightFrame, text="Bereit/Fertig").grid(column=4, row=5, sticky="w")
    self.led1 = Led(root=self.RightFrame, column=4, row=5, text="Bereit/Fertig", alpha=self.betriebszustand_0)
    self.led2 = Led(root=self.RightFrame, column=2, row=5, text="Pumpe an", alpha=self.pumpe_1)
    #Checkbutton(self.RightFrame, text="Pumpe").grid(column=2, row=5, sticky="w")

    ## row 6
    self.led3 = Led(root=self.RightFrame, column=2, row=6, text="Stillstand", alpha=self.trommel_0)
    self.led4 = Led(root=self.RightFrame, column=4, row=6, text="Waschen", alpha=self.betriebszustand_1)

    ## row 7
    self.led5 = Led(root=self.RightFrame, column=2, row=7, text="Rotieren", alpha=self.trommel_1)
    self.led6 = Led(root=self.RightFrame, column=4, row=7, text="Spülen", alpha=self.betriebszustand_2)

    ## row 8
    self.led7 = Led(root=self.RightFrame, column=2, row=8, text="Schleudern", alpha=self.trommel_2)
    self.led8 = Led(root=self.RightFrame, column=4, row=8, text="Schleudern", alpha=self.betriebszustand_3)

    threading.Thread(target=self.predicter()).start()
    self.root.update()

  def predicter(self):
    query = self.database.query(last=1)[0]
    trommel_probabilities = query["probabilities_trommel"]
    betriebszustand_probabilities = query["probabilities_betriebszustand"]
    pumpe_probabilities = query["probabilities_pumpe"]

    self.trommel_0.set(trommel_probabilities[0])
    self.trommel_1.set(trommel_probabilities[1])
    self.trommel_2.set(trommel_probabilities[2])

    self.betriebszustand_0.set(betriebszustand_probabilities[0])
    self.betriebszustand_1.set(betriebszustand_probabilities[1])
    self.betriebszustand_2.set(betriebszustand_probabilities[2])
    self.betriebszustand_3.set(betriebszustand_probabilities[3])

    self.pumpe_0.set(pumpe_probabilities[0])
    self.pumpe_1.set(pumpe_probabilities[1])

    # trommel
    self.led3.prob_value_string = "{} %".format(int(self.trommel_0.get() * 100))
    self.led3.alpha = self.trommel_0.get()
    self.led5.prob_value_string = "{} %".format(int(self.trommel_1.get() * 100))
    self.led5.alpha = self.trommel_1.get()
    self.led7.prob_value_string = "{} %".format(int(self.trommel_2.get() * 100))
    self.led7.alpha = self.trommel_2.get()

    # betriebszustand
    self.led1.prob_value_string = "{} %".format(int(self.betriebszustand_0.get() * 100))
    self.led1.alpha = self.betriebszustand_0.get()
    self.led4.prob_value_string = "{} %".format(int(self.betriebszustand_1.get() * 100))
    self.led4.alpha = self.betriebszustand_1.get()
    self.led6.prob_value_string = "{} %".format(int(self.betriebszustand_2.get() * 100))
    self.led6.alpha = self.betriebszustand_2.get()
    self.led8.prob_value_string = "{} %".format(int(self.betriebszustand_3.get() * 100))
    self.led8.alpha = self.betriebszustand_3.get()

    # pumpe
    self.led2.prob_value_string = "{} %".format(int(self.pumpe_1.get() * 100))
    self.led2.alpha = self.pumpe_1.get()

    self.led1.update()
    self.led2.update()
    self.led3.update()
    self.led4.update()
    self.led5.update()
    self.led6.update()
    self.led7.update()
    self.led8.update()

    keep_predicting = self.root.after(1000, self.predicter)

class Connection:
  def __init__(self, root, column, row):
    self.root = root
    self.column = column
    self.row = row
    self.state = False
    #self.text = "..."

    self.color = "#d9d9d9"

    size = 20
    x, y, r = size / 2, size / 2, size / 2
    self.canvas = Canvas(self.root, width=size, height=size)
    self.canvas.grid(column=self.column, row=self.row, sticky="w")
    self.circle = self.canvas.create_oval(x, y, x + r, y + r, fill=self.color, outline="#000000", width=1)

    self.label = Label(self.root, text="not connected")
    self.label.config(anchor=CENTER)
    self.label.grid(column=self.column+1, row=self.row, sticky="w")

  def update(self):
    if self.state:
      self.color = "#00ff00"
      self.label.config(text="connected")

    else:
      self.color = "#FE0000"

    self.canvas.itemconfig(self.circle, fill=self.color)

class Led:
  def __init__(self, root, column, row, text, alpha=None):
    self.root = root
    self.column = column
    self.row = row
    self.text = text
    self.prob_value = 0.
    self.prob_value_string = "{} %".format(int(self.prob_value*100))
    self.alpha = 0.

    self.color = "#d9d9d9"

    self.Frame = Frame(self.root)
    self.Frame.grid(row=self.row, column=self.column, sticky="w")

    size = 20
    x, y, r = size/2, size/2, size/2

    self.can = Canvas(self.Frame, width=size, height=size)
    self.can.grid(column=1, row=1, sticky="w")
    self.circle = self.can.create_oval(x, y, x+r, y+r, fill=self.color, outline="#000000", width=1)

    lbl = Label(self.Frame, text=self.text)
    lbl.config(anchor=CENTER)
    lbl.grid(column=3, row=1, sticky="w")

    self.prob = Label(self.Frame, text=self.prob_value_string)
    self.prob.config(anchor=CENTER)
    self.prob.grid(column=2, row=1, sticky="w")

  def update(self):
    self.set_color()
    self.prob.config(text=self.prob_value_string)

  def set_color(self):
    if self.alpha < 0.1:
      self.color = "#ffffff"
    elif self.alpha >= 0.1 and self.alpha < 0.2:
      self.color = "#e6ffe6"
    elif self.alpha >= 0.2 and self.alpha < 0.3:
      self.color = "#b3ffb3"
    elif self.alpha >= 0.3 and self.alpha < 0.4:
      self.color = "#99ff99"
    elif self.alpha >= 0.4 and self.alpha < 0.5:
      self.color = "#80ff80"
    elif self.alpha >= 0.5 and self.alpha < 0.6:
      self.color = "#66ff66"
    elif self.alpha >= 0.6 and self.alpha < 0.7:
      self.color = "#4dff4d"
    elif self.alpha >= 0.7 and self.alpha < 0.8:
      self.color = "#33ff33"
    elif self.alpha >= 0.8 and self.alpha < 0.9:
      self.color = "#19ff19"
    elif self.alpha >= 0.9 and self.alpha <= 1:
      self.color = "#00ff00"

    self.can.itemconfig(self.circle, fill=self.color)

class Tab_Control:
    def __init__(self,root):
        self.root = root
        self.root.title("DLSP Projekt")
        #self.root.geometry("1000x1400")
        self.root.configure(background="white")

        notebook = ttk.Notebook(self.root)
        self.TabControl1 = ttk.Frame(notebook)
        self.TabControl2 = ttk.Frame(notebook)
        self.TabControl3 = ttk.Frame(notebook)
        notebook.add(self.TabControl1, text='Überwachung')
        notebook.add(self.TabControl2, text='Training')
        #notebook.add(self.TabControl3, text='Details')
        notebook.grid()

        #--------------------- tabs -------------------------------------------
        tab1 = MonitoringTab(root=self.TabControl1)
        tab2 = TrainingTab(root=self.TabControl2)
        #tab3 = Plot(root=self.TabControl3)

class Frontend():
    root = Tk()
    application = Tab_Control(root)
    root.mainloop()

if __name__ == '__main__':
    Frontend()