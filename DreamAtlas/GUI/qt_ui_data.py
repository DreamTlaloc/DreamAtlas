THEME_FANTASY = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', sans-serif;
    font-size: 10pt;
}
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 4px;
    margin-top: 8px;
    font-weight: bold;
    color: #89b4fa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}
QTreeWidget {
    background-color: #181825;
    border: none;
    color: #cdd6f4;
}
QTreeWidget::item:selected {
    background-color: #313244;
}
QScrollBar:vertical {
    background: #181825;
    width: 10px;
}
QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 5px;
}
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 8px;
}
QPushButton:hover    { background-color: #45475a; }
QPushButton:checked  { background-color: #89b4fa; color: #1e1e2e; border-color: #89b4fa; }
QPushButton:disabled { color: #585b70; border-color: #313244; }
QCheckBox { spacing: 6px; }
QCheckBox::indicator {
    width: 14px; height: 14px;
    border: 1px solid #45475a;
    border-radius: 3px;
    background: #181825;
}
QCheckBox::indicator:checked { background: #89b4fa; }
QCheckBox:disabled { color: #585b70; }
QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
}
QMenuBar::item:selected { background-color: #313244; }
QMenu {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #45475a;
}
QMenu::item:selected { background-color: #313244; }
QSplitter::handle { background: #45475a; }
"""

THEME_VAMPIRE = """
QMainWindow, QWidget {
    background-color: #0d0d0d;
    color: #e0c8c8;
    font-family: 'Segoe UI', sans-serif;
    font-size: 10pt;
}
QGroupBox {
    border: 1px solid #5c2c2c;
    border-radius: 4px;
    margin-top: 8px;
    font-weight: bold;
    color: #c2455e;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}
QTreeWidget {
    background-color: #0a0a0a;
    border: none;
    color: #e0c8c8;
}
QTreeWidget::item:selected { background-color: #2a1010; }
QScrollBar:vertical { background: #0a0a0a; width: 10px; }
QScrollBar::handle:vertical { background: #5c2c2c; border-radius: 5px; }
QPushButton {
    background-color: #1a0a0a;
    color: #e0c8c8;
    border: 1px solid #5c2c2c;
    border-radius: 4px;
    padding: 4px 8px;
}
QPushButton:hover    { background-color: #2a1010; }
QPushButton:checked  { background-color: #c2455e; color: #0d0d0d; border-color: #c2455e; }
QPushButton:disabled { color: #3d2020; border-color: #1a0a0a; }
QCheckBox { spacing: 6px; }
QCheckBox::indicator {
    width: 14px; height: 14px;
    border: 1px solid #5c2c2c;
    border-radius: 3px;
    background: #0a0a0a;
}
QCheckBox::indicator:checked { background: #c2455e; }
QCheckBox:disabled { color: #3d2020; }
QMenuBar { background-color: #0a0a0a; color: #e0c8c8; }
QMenuBar::item:selected { background-color: #2a1010; }
QMenu {
    background-color: #0a0a0a;
    color: #e0c8c8;
    border: 1px solid #5c2c2c;
}
QMenu::item:selected { background-color: #2a1010; }
QSplitter::handle { background: #5c2c2c; }
"""