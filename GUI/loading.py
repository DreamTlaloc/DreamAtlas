import queue
import threading
from DreamAtlas import *
from DreamAtlas.GUI.ui_data import ART_ICON


class GeneratorLoadingWidget(ttk.Toplevel):

    def __init__(self, master, settings, map=None):
        super().__init__(title='Generating Map', iconphoto=ART_ICON, master=master, transient=master)
        self.map = map
        self.settings = settings
        self.grid()
        self.columnconfigure(0, minsize=500)
        self.rowconfigure(0, weight=1, minsize=30)
        self.rowconfigure(1, weight=1, minsize=15)
        self.progress_bar = ttk.Progressbar(self, maximum=100, mode='determinate', bootstyle='success', orient=ttk.HORIZONTAL, variable=ttk.IntVar())
        self.status_label_var = ttk.StringVar()
        self.status_label_var.set('Initialising...')
        self.status_label = ttk.Label(self, textvariable=self.status_label_var)
        self.progress_bar.grid(row=0, column=0, sticky='NEWS', pady=2)
        self.status_label.grid(row=1, column=0, sticky='NEWS', pady=2)

    def generate(self):

        self.master.map = generator_dreamatlas(settings=self.settings, ui=self)
        self.master.update_gui()
        self.destroy()
        # self.queue = queue.Queue()  # Some funky threading to make this work
        # self.generator = ThreadedGenerator(self.queue, self, self.settings).start()
        # self.after(100, self.process_queue)

    def process_queue(self):
        try:
            msg = self.queue.get_nowait()
            if msg == "Task finished":
                self.master.map = self.generator.map

                self.destroy()
        except queue.Empty:
            self.after(100, self.process_queue)


class ThreadedGenerator(threading.Thread):
    def __init__(self, queue, ui, settings):
        super().__init__()
        self.queue = queue
        self.ui = ui
        self.settings = settings

    def run(self):
        self.map = generator_dreamatlas(settings=self.settings, ui=self.ui, queue=self.queue)
        self.queue.put("Task finished")
