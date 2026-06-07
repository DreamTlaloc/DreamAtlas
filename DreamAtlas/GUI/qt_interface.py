import sys
from pathlib import Path
from PIL import Image
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter,
    QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTreeWidget, QTreeWidgetItem,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem,
    QCheckBox, QPushButton, QButtonGroup,
    QScrollArea, QLabel, QSizePolicy,
    QMenuBar, QMenu, QFileDialog, QAbstractItemView, QAction
)
from PyQt5.QtGui import (
    QPixmap, QImage, QColor, QPen, QBrush,
    QKeySequence
)
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal

from .qt_ui_data import THEME_FANTASY, THEME_VAMPIRE


class QtMainInterface(QMainWindow):
    x = 1


def run_qt_interface():
    app = QApplication(sys.argv)
    app.setStyleSheet(THEME_FANTASY)

    window = QtMainInterface()
    window.showMaximized()
    sys.exit(app.exec())
