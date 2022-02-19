from tkinter import *
import threading

from server.model import ClassifierModel
from src import gateway


class MonitoringTab:
  def __init__(self, root):
    self.chunk_length = 64
    self.trommel_classifier = ClassifierModel(chunk_length=self.chunk_length, model_name="trommel", label_column="Trommel")
    self.betriebszustand_classifier = ClassifierModel(chunk_length=self.chunk_length, model_name="betriebszustand", label_column="Betriebszustand")
    self.pumpe_classifier = ClassifierModel(chunk_length=self.chunk_length, model_name="pumpe", label_column="Pumpe")

    self.root = root
    self.database = gateway.Gateway(database="monitoring", collection="unlabeled")
    self.continuePredicting = False
    self.counter = 15000

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

    Button(self.RightFrame, text="Start/Stop", bg="red", fg="black", command=self.gui_inserting_handler).grid(column=2, row=10, columnspan=2)
    #self.connection = Connection(root=self.RightFrame, column=3, row=10)

  def change_predicting_state(self):
    if self.continuePredicting == True:
      self.continuePredicting = False
    else:
      self.continuePredicting = True

  def predicter(self):
    database = Training(database="monitoring", collection="ml_training")
    df = database.query(first=self.counter + self.chunk_length).iloc[self.counter:]
    print(df)
    trommel_probabilities = self.trommel_classifier.predict(df, counter = self.counter)[0]
    betriebszustand_probabilities = self.betriebszustand_classifier.predict(df, counter = self.counter)[0]
    pumpe_probabilities = self.pumpe_classifier.predict(df, counter = self.counter)[0]

    self.counter += 100

    print("Trommel",  trommel_probabilities)
    print("Betriebszustand",  betriebszustand_probabilities)
    print("Pumpe", pumpe_probabilities)

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
    self.led8.prob_value_string = "{} %".format(int(self.trommel_2.get() * 100))
    self.led8.alpha = self.trommel_2.get()

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

    if not self.continuePredicting:
      self.root.after_cancel(keep_predicting)

  def gui_inserting_handler(self):
    self.change_predicting_state()
    threading.Thread(target=self.predicter()).start()
    self.root.update()

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
