from tkinter import *
from tkinter import ttk
from gui.monitoringtab import MonitoringTab
from gui.plot import Plot
from gui.trainingtab import TrainingTab


class Tab_Control:
    def __init__(self,root):
        self.root = root
        self.root.title("DLSP Projekt")
        #self.root.geometry("1000x700")
        self.root.configure(background="white")

        notebook = ttk.Notebook(self.root)
        self.TabControl1 = ttk.Frame(notebook)
        self.TabControl2 = ttk.Frame(notebook)
        self.TabControl3 = ttk.Frame(notebook)
        notebook.add(self.TabControl1, text='Überwachung')
        notebook.add(self.TabControl2, text='Training')
        notebook.add(self.TabControl3, text='Details')
        notebook.grid()

        #--------------------- tabs -------------------------------------------
        tab1 = MonitoringTab(root=self.TabControl1)
        tab2 = TrainingTab(root=self.TabControl2)
        tab3 = Plot(root=self.TabControl3)

if __name__=='__main__':
    root = Tk()
    application = Tab_Control(root)
    root.mainloop()