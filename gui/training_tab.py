from tkinter import *

# these two imports are important
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
import threading

from gateway import gateway

continuePlotting = False

waschprogramm, gewicht, drehzahl = "default", 0., 0.
trommel, pumpe = 0, 0 # stillstand:0, rotieren:1, schleudern:1
betriebszustand = 0 # 0:bereit/fertig, 1:waschen, 2:spülen, 3:schleudern

program, f, w = "test", 1000, 3.1
database = gateway.Training(database = "monitoring",collection = "ml_training {}/{}/{}".format(program, f, w))

waschprogramme =  {
    0:"Default",
    1:"Pflegeleicht 30",
    2:"Pflegeleicht 40",
    3:"Pflegeleicht 60",
    4:"Koch/Buntwäsche 30",
    5:"Koch/Buntwäsche 40",
    6:"Koch/Buntwäsche 60",
    7:"Koch/Buntwäsche 60 Flecken",
    8:"Koch/Buntwäsche 90",
    9:"Quickmix 30",
    10:"Schleudern",
    11:"Abpumpen",
    12:"Wolle 30",
    13:"Wolle kalt",
    14:"Fein 30",}

def change_state():
    global continuePlotting
    if continuePlotting == True:
        continuePlotting = False
    else:
        continuePlotting = True


def data_points():
    df = database.query(last=100)
    x, y = df["datetime"] , df["A-mean"]
    return x, y


def app():
    # initialise a window.
    root = Tk()
    root.config(background='white')
    #root.geometry("1000x700")

    lab = Label(root, text="Live Plotting", bg='white')
    lab.grid(column=1, row=1)

    fig = Figure()

    ax1 = fig.add_subplot(211)
    ax1.set_title("Acceleration")
    ax1.set_xlabel("X axis")
    ax1.set_ylabel("Y axis")
    ax1.grid()

    ax2 = fig.add_subplot(212)
    ax2.set_title("Fourier")
    ax2.set_xlabel("X axis")
    ax2.set_ylabel("Y axis")
    ax2.grid()
    fig.set_tight_layout(True)

    graph = FigureCanvasTkAgg(fig, master=root)
    graph.get_tk_widget().grid(column=1, row=1, columnspan=1, rowspan=8)

    def entry(text, column, row):
        label = Label(text=text, font=("Helvetica", "14", "bold", "underline"))
        label.grid(column=column, row=row, sticky="w")
        entry = Entry(width=4)
        entry.grid(column=column+1, row=row, sticky="w")

    def plotter():
        while continuePlotting:
            ax1.cla()
            ax1.grid()
            x, y = data_points()
            ax1.plot(x, y, marker='o', color='orange')
            ax2.plot(gateway.Gateway.fft_peaks(y), marker='o', color='orange')
            graph.draw()
            time.sleep(1)

    def gui_handler():
        change_state()
        threading.Thread(target=plotter).start()


    label_waschprogramme = Label(text="Waschprogramm:", font=("Helvetica", "14", "bold", "underline")).grid(column=2, row=1)

    clicked = StringVar()
    clicked.set("Default")

    dropdown = OptionMenu(root, clicked, *waschprogramme.values())
    dropdown.config(width=15)
    dropdown.grid(column=3, row=1, columnspan=2)

    ## row 2
    entry("Gewicht in (kg):", column=2, row=2)

    ## row 3
    entry("Drehzahl:", column=2, row=3)

    ## row 4
    Label(text="Vorgang", font=("Helvetica", "14", "bold", "underline")).grid(column=2, row=4, columnspan=2)
    Label(text="Betriebszustand", font=("Helvetica", "14", "bold", "underline")).grid(column=4, row=4)

    ## row 5

    ## row 6
    Radiobutton(text="Stillstand").grid(column=2, row=6, sticky="w")
    Radiobutton(text="Waschen").grid(column=4, row=6, sticky="w")

    ## row 7
    Radiobutton(text="Rotieren").grid(column=2, row=7, sticky="w")
    Radiobutton(text="Spülen").grid(column=4, row=7, sticky="w")

    ## row 8
    Radiobutton(text="Schleudern").grid(column=2, row=8, sticky="w")
    Radiobutton(text="Schleudern").grid(column=4, row=8, sticky="w")

    ## row 9
    Radiobutton(text="Bereit/Fertig").grid(column=4, row=9, sticky="w")
    Checkbutton(text="Pumpe").grid(column=2, row=9, sticky="w")

    ## row 10
    start_button = Button(root, text="Start/Stop", command=gui_handler, bg="red", fg="black")
    start_button.grid(column=2, row=10, columnspan=3)

    root.mainloop()

if __name__ == '__main__':
    app()