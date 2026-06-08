import threading
import queue

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QProgressBar, QLabel
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal

from ..generators import generator_dreamatlas


class GeneratorThread(QThread):  # Worker thread — replaces ThreadedGenerator

    # Emitted when progress updates: (percent, status_message)
    progress_updated = pyqtSignal(int, str)

    # Emitted when generation is fully complete
    finished = pyqtSignal(object)  # carries the completed map

    def __init__(self, settings, ui):
        super().__init__()
        self.settings = settings
        self.ui = ui
        self.map = None

    def run(self):
        # generator_dreamatlas is expected to call self.ui.update_progress()
        self.map = generator_dreamatlas(settings=self.settings, ui=None)
        self.finished.emit(self.map)


class QtGeneratorLoadingWidget(QDialog):

    def __init__(self, master, settings, map=None):
        super().__init__(master)

        self.map = map
        self.settings = settings
        self._thread = None

        self.setWindowTitle('Generating Map')
        self.setWindowIcon(master.windowIcon())

        self.setWindowFlags(  # Prevent the user from closing the dialog mid-generation
            self.windowFlags() & ~Qt.WindowContextHelpButtonHint
        )

        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel('Initialising...')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(15)
        layout.addWidget(self.status_label)

        self.show()

    def generate(self):
        self._thread = GeneratorThread(settings=self.settings, ui=self)
        self._thread.progress_updated.connect(self._on_progress)
        self._thread.finished.connect(self._on_finished)
        self._thread.start()

    def _on_progress(self, percent: int, message: str):
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)

    def _on_finished(self, completed_map):
        parent = self.parent()
        if parent is not None:
            parent.map = completed_map
            parent.update_gui()
        self.accept()  # closes the dialog

    def update_progress(self, percent: int, message: str = ''):
        if self._thread is not None:
            self._thread.progress_updated.emit(percent, message)
