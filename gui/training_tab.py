from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
import threading

from src import gateway

continuePlotting = False
continueInserting = False

database = gateway.Training(database ="monitoring", collection ="ml_training")

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

def change_plotting_state():
    global continuePlotting
    if continuePlotting == True:
        continuePlotting = False
    else:
        continuePlotting = True

def change_inserting_state():
    global continueInserting
    if continueInserting == True:
        continueInserting = False
    else:
        continueInserting = True

def data_points():
    df = database.query(last=100)
    x, y = df["datetime"] , df["A-mean"]
    return x, y


def app():
    # initialise a window.
    root = Tk()
    root.config(background='white')
    #root.geometry("1000x700")

    waschprogramm = StringVar()
    gewicht = DoubleVar()
    drehzahl = StringVar()
    trommel = IntVar()
    pumpe = IntVar()
    betriebszustand = IntVar()

    waschprogramm.set("Default")
    gewicht.set(0.)
    drehzahl.set(0.)
    trommel.set(0)  # stillstand:0, rotieren:1, schleudern:1
    pumpe.set(0)
    betriebszustand.set(0)  # 0:bereit/fertig, 1:waschen, 2:spülen, 3:schleudern

    lab = Label(root, text="Live Plotting", bg='white')
    lab.grid(column=1, row=1)

    fig = Figure()

    ax1 = fig.add_subplot(211)
    ax1.set_title("Acceleration")
    ax1.set_xlabel("time")
    ax1.set_ylabel("Acceleration in (g)")
    ax1.grid()
    ax1.plot([], [], marker='o', color='orange')

    ax2 = fig.add_subplot(212)
    ax2.set_title("Fourier")
    ax2.set_xlabel("X axis")
    ax2.set_ylabel("Y axis")
    ax2.grid()
    ax2.plot([], [], marker='o', color='orange')
    fig.set_tight_layout(True)

    graph = FigureCanvasTkAgg(fig, master=root)
    graph.get_tk_widget().grid(column=1, row=1, columnspan=1, rowspan=8)

    def entry(text, column, row, variable=None):
        label = Label(text=text, font=("Helvetica", "14", "bold", "underline"))
        label.grid(column=column, row=row, sticky="w")

        entry = Entry(width=4, textvariable=variable)
        entry.grid(column=column+1, row=row, sticky="w")

    def plotter():
        while continuePlotting:
            #ax1.cla()
            #ax1.grid()
            x, y = data_points()
            ax1.plot(x, y, marker='o', color='orange')
            ax2.plot(gateway.Gateway.fft_peaks(y), marker='o', color='orange')

            graph.draw()
            time.sleep(1)


    def inserter():
        connected = False
        print("Connecting to device...")
        while continueInserting:
            while not connected:
                try:
                    parameters = {
                        "Waschprogramm": waschprogramm.get(),
                        "Gewicht": gewicht.get(),
                        "Drehzahl": drehzahl.get(),
                        "Trommel": trommel.get(),
                        "Pumpe": pumpe.get(),
                        "Betriebszustand": betriebszustand.get(),
                    }
                    database.fill_db(parameters=parameters)
                    connected = True
                except:
                    print("Connection to device failed")
                    time.sleep(1)
            print("Waschprogramm: {}, Gewicht: {} kg, Drehzahl: {}".format(waschprogramm.get(), gewicht.get(),
                                                                           drehzahl.get()))
            print("Trommel: {}, Pumpe: {}, Betriebszustand: {}".format(trommel.get(), pumpe.get(),
                                                                      betriebszustand.get()))
            print("stopped Inserting")


    def gui_plotting_handler():
        change_plotting_state()
        threading.Thread(target=plotter).start()

    def gui_inserting_handler():
        change_inserting_state()
        threading.Thread(target=inserter).start()

    Label(text="Waschprogramm:", font=("Helvetica", "14", "bold", "underline")).grid(column=2, row=1)

    dropdown = OptionMenu(root, waschprogramm, *waschprogramme.values())
    dropdown.config(width=15)
    dropdown.grid(column=3, row=1, columnspan=2)

    ## row 2
    entry("Gewicht in (kg):", column=2, row=2, variable=gewicht)

    ## row 3
    entry("Drehzahl:", column=2, row=3, variable=drehzahl)

    ## row 4
    Label(text="Vorgang", font=("Helvetica", "14", "bold", "underline")).grid(column=2, row=4)
    Label(text="Betriebszustand", font=("Helvetica", "14", "bold", "underline")).grid(column=4, row=4)

    ## row 5
    Radiobutton(text="Bereit/Fertig", variable=betriebszustand, value=0).grid(column=4, row=5, sticky="w")
    Checkbutton(text="Pumpe", variable=pumpe).grid(column=2, row=5, sticky="w")

    ## row 6
    Radiobutton(text="Stillstand", variable=trommel, value=0).grid(column=2, row=6, sticky="w")
    Radiobutton(text="Waschen", variable=betriebszustand, value=1).grid(column=4, row=6, sticky="w")

    ## row 7
    Radiobutton(text="Rotieren", variable=trommel, value=1).grid(column=2, row=7, sticky="w")
    Radiobutton(text="Spülen", variable=betriebszustand, value=2).grid(column=4, row=7, sticky="w")

    ## row 8
    Radiobutton(text="Schleudern", variable=trommel, value=2).grid(column=2, row=8, sticky="w")
    Radiobutton(text="Schleudern", variable=betriebszustand, value=3).grid(column=4, row=8, sticky="w")

    ## row 9
    Button(root, text="Start/Stop Plotting", command=gui_plotting_handler, bg="red", fg="black").grid(column=2, row=9, columnspan=1)
    Button(root, text="Start/Stop Inserting", command=gui_inserting_handler, bg="red", fg="black").grid(column=4, row=9, columnspan=1)

    root.mainloop()

if __name__ == '__main__':
    app()