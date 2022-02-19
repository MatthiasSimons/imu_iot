from tkinter import *
import threading
from src import gateway


class TrainingTab:
    def __init__(self, root):
        self.root = root

        self.database = gateway.Training(database="monitoring", collection="ml_training")
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

        #plot = Plot(self.LeftFrame)

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
        conn = self.database.listen_socket()
        i=0

        while self.continueInserting:# and self.database.received() is not None:
            parameters = {
                "Waschprogramm": self.waschprogramm.get(),
                "Gewicht": self.gewicht.get(),
                "Drehzahl": self.drehzahl.get(),
                "Trommel": self.trommel.get(),
                "Pumpe": self.pumpe.get(),
                "Betriebszustand": self.betriebszustand.get(),
            }
            self.database.write(conn, parameters=parameters)
            print(i, parameters)

        # print("Connecting to device...")
        # while self.continueInserting:
        #     print("test1")
        #     parameters = {
        #         "Waschprogramm": self.waschprogramm.get(),
        #         "Gewicht": self.gewicht.get(),
        #         "Drehzahl": self.drehzahl.get(),
        #         "Trommel": self.trommel.get(),
        #         "Pumpe": self.pumpe.get(),
        #         "Betriebszustand": self.betriebszustand.get(),
        #     }
        #     self.database.fill_db(parameters=parameters)

            # print("Waschprogramm: {}, Gewicht: {} kg, Drehzahl: {}".format(self.waschprogramm.get(), self.gewicht.get(),
            #                                                                self.drehzahl.get()))
            # print("Trommel: {}, Pumpe: {}, Betriebszustand: {}".format(self.trommel.get(), self.pumpe.get(),
            #                                                            self.betriebszustand.get()))
            # print("stopped Inserting")
            if not self.continueInserting:
                self.database.close_connection()

    def gui_inserting_handler(self):
        self.change_inserting_state()
        threading.Thread(target=self.inserter).start()



