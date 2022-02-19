from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
import threading
from src import gateway


class Plot:
    def __init__(self, root):
        self.root = root
        self.database = gateway.Training(database="monitoring", collection="ml_training")

        self.continuePlotting = True

        fig = Figure()

        self.ax1 = fig.add_subplot(211)
        self.ax1.set_title("Acceleration")
        self.ax1.set_xlabel("time")
        self.ax1.set_ylabel("Acceleration in (g)")
        self.ax1.grid()
        self.ax1.plot([], [], marker='o', color='orange')

        self.ax2 = fig.add_subplot(212)
        self.ax2.set_title("Fourier")
        self.ax2.set_xlabel("Frequency in (Hz)")
        self.ax2.set_ylabel("FFT(T)")
        self.ax2.grid()
        self.ax2.plot([], [], marker='o', color='orange')
        fig.set_tight_layout(True)

        self.graph = FigureCanvasTkAgg(fig, master=self.root)
        self.graph.get_tk_widget().grid(column=1, row=2)
        self.gui_plotting_handler()

    def plotter(self):
        while self.continuePlotting == True:
            x, y = self.data_points()
            #x = pd.to_datetime(x, format='%Y/%M/%D  %H:%M:%S:%f')
            self.ax1.plot(x, y, marker='o', color='orange')
            self.ax1.xaxis.set_tick_params(rotation=45)
            # spacing = 2
            # visible = self.ax1.xaxis.get_ticklabels()[::spacing]
            # for label in self.ax1.xaxis.get_ticklabels():
            #     if label not in visible:
            #         label.set_visible(False)

            self.ax2.plot(self.database.fft_peaks(a=y,peaks=None), marker='o', color='orange')

            self.graph.draw()
            time.sleep(1)

    def change_plotting_state(self):
        if self.continuePlotting == True:
            self.continuePlotting = False
        else:
            self.continuePlotting = True

    def gui_plotting_handler(self):
        #self.change_plotting_state()
        threading.Thread(target=self.plotter).start()

    def data_points(self):
      df = self.database.query(last=256)
      x, y = df["datetime"], df["A"]
      return x, y

