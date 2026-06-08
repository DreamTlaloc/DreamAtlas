from .qt_loading import QtGeneratorLoadingWidget
from ..databases import (AGES, LOAD_DIR, AGE_NATIONS, VICTORY_CONDITIONS, POPTYPES, FORT, SPECIAL_NEIGHBOUR,
                         REGION_WATER_INFO, REGION_CAVE_INFO, AGE_POPULATION_MODIFIERS, NOT_AVAILABLE_GRAPHS, DATASET_GRAPHS)
from ..functions import has_terrain

from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QScrollArea, QLabel, QLineEdit, QComboBox, QPushButton, QSlider, QSizePolicy, QFileDialog, QGraphicsView, QGraphicsScene
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIntValidator

from .ui_data import *


class MapCanvas(QGraphicsView):
    """
    Scrollable, pannable graphics view used as the main map viewport.
    Replaces the tkinter Canvas. Items are stored in a QGraphicsScene;
    visibility is managed via item.setVisible().
    """

    province_right_clicked = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        # Pan with left-button drag
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setRenderHint(self.renderHints())

        # Internal lookup structures populated by update_viewing_panel()
        self._bitmaps = {}  # plane → list of (index, QGraphicsPixmapItem, QPixmap)
        self._bitmap_colors = {}  # plane → list of colour strings per lense
        self._photoimages = {}  # plane → (path, QGraphicsPixmapItem, normal_px, trans_px) | None
        self._connections = {}  # plane → list of (connection_obj, QGraphicsLineItem)
        self._nodes = {}  # plane → list of (province_index, QGraphicsEllipseItem)
        self._borders = {}  # plane → (QGraphicsPixmapItem, QPixmap)
        self._icons = {}  # plane → list of QGraphicsPixmapItem

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            scene_pos = self.mapToScene(event.pos())
            items = self._scene.items(scene_pos)
            if items:
                item = items[0]
                data = item.data(0)  # we store Province/Connection in data slot 0
                if data is not None:
                    self.province_right_clicked.emit(data)
        else:
            super().mousePressEvent(event)

    def scroll_to_fraction(self, fx: float, fy: float):
        h_bar = self.horizontalScrollBar()
        v_bar = self.verticalScrollBar()
        h_bar.setValue(int(fx * h_bar.maximum()))
        v_bar.setValue(int(fy * v_bar.maximum()))

    def set_visible_plane(self, plane: int, all_planes):
        for p in all_planes:
            visible = (p == plane)
            for item in self._scene.items():
                if item.data(1) == p:  # data slot 1 = plane index
                    item.setVisible(visible)

    def clear_scene(self):
        self._scene.clear()
        self._bitmaps.clear()
        self._bitmap_colors.clear()
        self._photoimages.clear()
        self._connections.clear()
        self._nodes.clear()
        self._borders.clear()
        self._icons.clear()


class QtInputToplevel(QDialog):

    def __init__(self, master, title, ui_config, target_type=None,
                 target_class=None, target_location=None, map=None,
                 parent_widget=None, geometry=""):
        super().__init__(master)
        self.setWindowTitle(title)
        self.setWindowIcon(master.windowIcon())

        # Parse "WxH" geometry string if provided
        if geometry:
            try:
                w, h = geometry.split('x')
                self.resize(int(w), int(h))
            except ValueError:
                pass

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.widget = QtInputWidget(
            master=self,
            ui_config=ui_config,
            target_type=target_type,
            target_class=target_class,
            target_location=target_location,
            map=map,
            parent_widget=parent_widget,
        )
        layout.addWidget(self.widget)

        if target_class is not None:
            self.widget.class_2_input()

        self.show()


class QtInputWidget(QWidget):

    def __init__(self, master, ui_config, target_type=None, target_class=None, target_location=None, map=None,
                 parent_widget=None):
        super().__init__(master)

        self.ui_config = ui_config
        self.target_class = target_class if target_class is not None else type(target_type)
        self.target_location = target_location
        self.map = map
        self.parent_widget = parent_widget

        self.labels = {}
        self.inputs = {}
        self.variables = {}

        # Button definitions: [label, callback]
        self.BUTTONS = [
            ['Update', self.update_class],
            ['Add', self.add],
            ['Generate', self.generate],
            ['Save', self.save],
            ['Load', self.load],
            ['Reset', self.clear],
            ['Close', self._close],
        ]

        self.frames = []
        self.cols = 0
        self.nation_cols = 0

        self._make_gui()
        self._make_size()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._make_size()

    def _make_size(self):
        width = self._scroll_area.viewport().width() if hasattr(self, '_scroll_area') else self.width()
        new_small_cols = max(1, width // INPUT_ENTRY_SIZE)
        new_nation_cols = max(1, int(width / 120))

        for frame_box in self.frames:
            layout = frame_box.layout()
            if layout is None:
                continue
            for idx in range(layout.count()):
                child = layout.itemAt(idx).widget()
                if isinstance(child, CustomGenericNationWidget):
                    child.update(cols=new_small_cols)
                    break

        if self.cols != new_small_cols:
            self.cols = new_small_cols
            for frame_box in self.frames:
                layout = frame_box.layout()
                if not isinstance(layout, QGridLayout):
                    continue
                widgets_to_reflow = []
                for idx in range(layout.count()):
                    w = layout.itemAt(idx).widget()
                    if w and not isinstance(w, (VanillaNationWidget, CustomGenericNationWidget, TerrainWidget)):
                        widgets_to_reflow.append(w)
                for idx, w in enumerate(widgets_to_reflow):
                    layout.addWidget(w, idx // self.cols, idx % self.cols)

        if self.nation_cols != new_nation_cols:
            self.nation_cols = new_nation_cols
            for frame_box in self.frames:
                layout = frame_box.layout()
                if layout is None:
                    continue
                for idx in range(layout.count()):
                    w = layout.itemAt(idx).widget()
                    if isinstance(w, (VanillaNationWidget, CustomGenericNationWidget)):
                        disciples = self.variables.get('disciples', 0)
                        w.update(disciples, cols=new_nation_cols)
                    elif isinstance(w, TerrainWidget):
                        w.update(cols=new_nation_cols)

    def _make_gui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        self._scroll_layout = QVBoxLayout(scroll_content)
        self._scroll_layout.setSpacing(2)
        self._scroll_layout.setContentsMargins(4, 4, 4, 4)
        self._scroll_area.setWidget(scroll_content)
        root_layout.addWidget(self._scroll_area, stretch=1)

        # Build label frames
        for index, (text, attributes) in enumerate(self.ui_config['label_frames']):
            group = QGroupBox(text)
            group_layout = QGridLayout(group)
            group_layout.setSpacing(2)
            group_layout.setContentsMargins(4, 8, 4, 4)
            self.frames.append(group)
            self._scroll_layout.addWidget(group)

            for i, attribute in enumerate(attributes):

                if attribute == 'generation_info':
                    info = GeneratorInfoWidget(group)
                    group_layout.addWidget(info, 0, 0)
                    break

                _, widget, label, options, active, tooltip = self.ui_config['attributes'][attribute]

                if widget == 4:
                    w = VanillaNationWidget(group)
                    self.inputs['vanilla_nations'] = w
                    group_layout.addWidget(w, i // max(self.cols, 1), i % max(self.cols, 1))

                elif widget == 5:
                    w = CustomGenericNationWidget(group)
                    self.inputs['custom_nations'] = w
                    group_layout.addWidget(w, i // max(self.cols, 1), i % max(self.cols, 1))

                elif widget == 6:
                    w = IllwinterDropdownWidget(group, attribute)
                    self.inputs[attribute] = w
                    group_layout.addWidget(w, i // max(self.cols, 1), i % max(self.cols, 1))

                elif widget == 7:
                    w = TerrainWidget(group)
                    self.inputs[attribute] = w
                    group_layout.addWidget(w, i // max(self.cols, 1), i % max(self.cols, 1))

                else:
                    miniframe = QWidget(group)
                    mini_layout = QGridLayout(miniframe)
                    mini_layout.setContentsMargins(0, 0, 0, 0)
                    mini_layout.setSpacing(2)
                    mini_layout.setColumnMinimumWidth(0, 100)
                    mini_layout.setColumnMinimumWidth(1, 100)
                    mini_layout.setColumnStretch(0, 1)
                    mini_layout.setColumnStretch(1, 1)

                    lbl = QLabel(label)
                    lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    lbl.setToolTip(tooltip)
                    mini_layout.addWidget(lbl, 0, 0)
                    self.labels[attribute] = lbl

                    if widget == 0:
                        inp = QLineEdit()
                        inp.setEnabled(active)
                        inp.setToolTip(tooltip)
                        self.inputs[attribute] = inp
                        mini_layout.addWidget(inp, 0, 1)

                    elif widget == 1:
                        inp = QComboBox()
                        inp.addItems(options)
                        inp.setEnabled(True)  # always readable
                        inp.setToolTip(tooltip)
                        self.inputs[attribute] = inp
                        mini_layout.addWidget(inp, 0, 1)

                    elif widget == 2:
                        inp = EntryScaleWidget(miniframe, from_=options[0], to=options[1], enabled=active)
                        inp.set(options[0])
                        inp.setToolTip(tooltip)
                        self.inputs[attribute] = inp
                        mini_layout.addWidget(inp, 0, 1)

                    elif widget == 3:
                        self.variables[attribute] = 0
                        inp = QPushButton()
                        inp.setCheckable(True)
                        inp.setEnabled(active)
                        inp.setToolTip(tooltip)
                        if attribute == 'disciples':
                            inp.toggled.connect(lambda checked: self._set_variable(attribute, int(checked)))
                            inp.toggled.connect(self.update_disciples)
                        else:
                            inp.toggled.connect(lambda checked, a=attribute: self._set_variable(a, int(checked)))
                        inp.setText('●')  # visual toggle indicator
                        self.inputs[attribute] = inp
                        mini_layout.addWidget(inp, 0, 1)

                    group_layout.addWidget(miniframe, i // max(self.cols, 1), i % max(self.cols, 1))

        # Button bar
        if len(self.ui_config['buttons']) > 0:
            button_bar = QWidget()
            bar_layout = QHBoxLayout(button_bar)
            bar_layout.setContentsMargins(2, 2, 2, 2)
            bar_layout.setSpacing(2)

            for btn_index in self.ui_config['buttons']:
                label, callback = self.BUTTONS[btn_index]
                btn = QPushButton(label)
                btn.clicked.connect(callback)
                bar_layout.addWidget(btn)

            root_layout.addWidget(button_bar, stretch=0)

    def _set_variable(self, attribute, value):
        self.variables[attribute] = value

    def _close(self):
        parent = self.parent()
        if parent:
            parent.close()

    def update_disciples(self):
        disciples = self.variables.get('disciples', 0)
        if 'vanilla_nations' in self.inputs:
            self.inputs['vanilla_nations'].update(disciples=disciples)
        if 'custom_nations' in self.inputs:
            self.inputs['custom_nations'].update(disciples=disciples)

    def input_2_class(self):
        for attribute, (attribute_type, widget, _, options, active, __) in self.ui_config['attributes'].items():
            if not active:
                continue
            if widget == 0:
                setattr(self.target_class, attribute, attribute_type(self.inputs[attribute].text()))
            elif widget == 1:
                setattr(self.target_class, attribute, attribute_type(self.inputs[attribute].currentIndex()))
            elif widget == 2:
                setattr(self.target_class, attribute, attribute_type(self.inputs[attribute].get()))
            elif widget == 3:
                setattr(self.target_class, attribute, attribute_type(self.variables.get(attribute, 0)))
            elif widget == 4:
                self.target_class.age = AGES.index(self.inputs['vanilla_nations'].age.currentText())
                self.target_class.vanilla_nations = self.inputs['vanilla_nations'].get()
            elif widget == 5:
                self.target_class.custom_nations = self.inputs['custom_nations'].custom_nation_list
                self.target_class.generic_nations = self.inputs['custom_nations'].generic_nation_list
            elif widget == 6:
                setattr(self.target_class, attribute, attribute_type(self.inputs[attribute].get()))
            elif widget == 7:
                self.target_class.terrain_int = int(self.inputs['terrain_int'].terrain_int)

    def class_2_input(self):
        for attribute, (attribute_type, widget, _, options, active, ___) in self.ui_config['attributes'].items():
            value = getattr(self.target_class, attribute, None)
            if value is None:
                continue

            if widget == 0:
                inp = self.inputs[attribute]
                inp.setEnabled(True)
                inp.setText(str(value))
                if not active:
                    inp.setEnabled(False)
            elif widget == 1:
                idx = options.index(value) if value in options else value
                self.inputs[attribute].setCurrentIndex(idx)
            elif widget == 2:
                self.inputs[attribute].set(value)
            elif widget == 3:
                self.variables[attribute] = int(value)
                self.inputs[attribute].setChecked(bool(value))
            elif widget == 4:
                age_name = AGES[getattr(self.target_class, 'age')]
                self.inputs['vanilla_nations'].age.setCurrentText(age_name)
                self.inputs['vanilla_nations'].vanilla_nation_list = value
                self.inputs['vanilla_nations'].update(disciples=getattr(self.target_class, 'disciples', 0))
            elif widget == 5:
                self.inputs['custom_nations'].custom_nation_list = getattr(self.target_class, 'custom_nations', [])
                self.inputs['custom_nations'].generic_nation_list = getattr(self.target_class, 'generic_nations', [])
                self.inputs['custom_nations'].update(disciples=getattr(self.target_class, 'disciples', 0))
            elif widget == 6:
                self.inputs[attribute].set(self.inputs[attribute].set_dict.get(value, '-'))
            elif widget == 7:
                self.inputs[attribute].terrain_int = getattr(self.target_class, 'terrain_int', 0)
                self.inputs[attribute].update(cols=self.cols * 2,
                                              set_terrain=getattr(self.target_class, 'terrain_int', 0))

    def input_2_list(self):
        input_list = []
        for attribute, (attribute_type, widget, _, options, active, __) in self.ui_config['attributes'].items():
            if not active:
                continue
            if widget == 0:
                input_list.append(self.inputs[attribute].text())
            elif widget == 1:
                if attribute == 'home_plane':
                    input_list.append(1 + self.inputs[attribute].currentIndex())
                else:
                    input_list.append(self.inputs[attribute].currentIndex())
            elif widget == 7:
                input_list.append(self.inputs['terrain'].terrain_int)
        input_list.append(1)  # temporary fix for teams
        return input_list

    def update_class(self):
        self.input_2_class()

    def add(self):
        self.target_location.append(self.input_2_list())
        if self.parent_widget:
            self.parent_widget.update()
        parent = self.parent()
        if parent:
            parent.close()

    def generate(self):
        self.input_2_class()
        loader = QtGeneratorLoadingWidget(master=self.parent().parent(), map=self.map, settings=self.target_class)
        loader.generate()
        parent = self.parent()
        if parent:
            parent.close()

    def save(self):
        self.input_2_class()
        path, _ = QFileDialog.getSaveFileName(self, "Save File", str(LOAD_DIR))
        if path:
            self.target_class.save_file(path)

    def load(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load File", str(LOAD_DIR))
        if path:
            self.target_class.load_file(path)
            self.class_2_input()

    def clear(self):
        # Rebuild the widget in place
        parent = self.parent()
        layout = parent.layout()
        old_idx = None
        if layout:
            for i in range(layout.count()):
                if layout.itemAt(i).widget() is self:
                    old_idx = i
                    break
        self.deleteLater()
        new_widget = QtInputWidget(parent, self.ui_config, target_class=self.target_class)
        new_widget.class_2_input()
        if layout and old_idx is not None:
            layout.insertWidget(old_idx, new_widget)


class VanillaNationWidget(QWidget):

    def __init__(self, master):
        super().__init__(master)
        self.cols = 4
        self.disciples = 0
        self.vanilla_nation_list = []
        self.options = {}
        self.variables = {}
        self.teams = {}
        self.miniframes = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)

        self.age = QComboBox()
        self.age.addItems(AGES)
        self.age.setCurrentText(AGES[0])
        self.age.currentIndexChanged.connect(lambda: self.update())
        main_layout.addWidget(self.age)

        self._grid_widget = QWidget()
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setSpacing(2)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._grid_widget)

        self.update()

    def update(self, disciples=None, cols=None):
        if disciples is not None:
            self.disciples = disciples
        if cols is not None:
            self.cols = cols

        self.options.clear()
        self.variables.clear()
        self.teams.clear()

        for frame in self.miniframes:
            frame.deleteLater()
        self.miniframes.clear()

        age_index = AGES.index(self.age.currentText())

        for i, entry in enumerate(AGE_NATIONS[age_index]):
            nation_id, nation_name = entry[0], entry[1]

            mf = QWidget(self._grid_widget)
            mf_layout = QHBoxLayout(mf)
            mf_layout.setContentsMargins(0, 0, 0, 0)
            mf_layout.setSpacing(1)
            self.miniframes.append(mf)
            self._grid_layout.addWidget(mf, i // self.cols, i % self.cols)

            btn = QPushButton(nation_name)
            btn.setCheckable(True)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.options[nation_id] = btn
            self.variables[nation_id] = False
            btn.toggled.connect(lambda checked, nid=nation_id: self._set_nation(nid, checked))
            mf_layout.addWidget(btn, stretch=4)

            if self.disciples:
                team_cb = QComboBox()
                team_cb.addItems([str(t) for t in TEAMS])
                team_cb.setMaximumWidth(40)
                self.teams[nation_id] = team_cb
                mf_layout.addWidget(team_cb, stretch=1)

            # Restore previously selected state
            for nation, team in self.vanilla_nation_list:
                if nation_id == nation:
                    btn.setChecked(True)
                    if self.disciples and nation_id in self.teams:
                        self.teams[nation_id].setCurrentText(str(team))

    def _set_nation(self, nation_id, checked):
        self.variables[nation_id] = checked

    def get(self):
        nation_list = []
        age_index = AGES.index(self.age.currentText())
        for entry in AGE_NATIONS[age_index]:
            nation_id = entry[0]
            if self.variables.get(nation_id, False):
                team = 0
                if self.disciples and nation_id in self.teams:
                    team = int(self.teams[nation_id].currentText())
                nation_list.append([nation_id, team])
        return nation_list


class CustomGenericNationWidget(QWidget):

    def __init__(self, master):
        super().__init__(master)
        self.cols = 4
        self.disciples = 0
        self.nation_inputs = {}
        self.custom_nation_list = []
        self.generic_nation_list = []
        self.miniframes = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)

        btn_row = QWidget()
        btn_row_layout = QHBoxLayout(btn_row)
        btn_row_layout.setContentsMargins(0, 0, 0, 0)

        add_custom = QPushButton('Add Custom Nation')
        add_custom.clicked.connect(lambda: QtInputToplevel(
            self, 'Add Custom Nation', UI_CONFIG_CUSTOMNATION, 1,
            target_location=self.custom_nation_list,
            parent_widget=self, geometry="500x550"
        ))
        add_generic = QPushButton('Add Generic Start')
        add_generic.clicked.connect(lambda: QtInputToplevel(
            self, 'Add Generic Start', UI_CONFIG_GENERICNATION, 1,
            target_location=self.generic_nation_list,
            parent_widget=self, geometry="400x450"
        ))
        btn_row_layout.addWidget(add_custom)
        btn_row_layout.addWidget(add_generic)
        main_layout.addWidget(btn_row)

        self._grid_widget = QWidget()
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setSpacing(2)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._grid_widget)

        self.update()

    def update(self, disciples=None, cols=None):
        if disciples is not None:
            self.disciples = disciples
        if cols is not None:
            self.cols = cols

        for frame in self.miniframes:
            frame.deleteLater()
        self.miniframes.clear()
        self.nation_inputs.clear()

        styles = ['color: #28a745', 'color: #6c757d']  # success / secondary colours

        for i, nation_list in enumerate([self.custom_nation_list, self.generic_nation_list]):
            for j, nation in enumerate(nation_list):
                count = i * len(self.custom_nation_list) + j

                mf = QWidget(self._grid_widget)
                mf_layout = QHBoxLayout(mf)
                mf_layout.setContentsMargins(0, 0, 0, 0)
                mf_layout.setSpacing(1)
                self.miniframes.append(mf)
                self._grid_layout.addWidget(mf, count // self.cols, count % self.cols)

                text = nation[1] if i == 0 else f'Generic Nation {j + 1}'
                nation_btn = QPushButton(text)
                nation_btn.setStyleSheet(styles[i])
                nation_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                self.nation_inputs[count] = nation_btn
                mf_layout.addWidget(nation_btn, stretch=5)

                if self.disciples:
                    team_cb = QComboBox()
                    team_cb.addItems([str(t) for t in TEAMS])
                    team_cb.setMaximumWidth(40)
                    mf_layout.addWidget(team_cb, stretch=1)

                remove_btn = QPushButton('X')
                remove_btn.setMaximumWidth(28)
                remove_btn.setStyleSheet(styles[i])
                target_list = self.custom_nation_list if i == 0 else self.generic_nation_list
                remove_btn.clicked.connect(lambda _, lst=target_list, idx=j: self.remove(lst, idx))
                mf_layout.addWidget(remove_btn, stretch=1)

    def remove(self, nation_list, j):
        if 0 <= j < len(nation_list):
            nation_list.pop(j)
        self.update()


class EntryScaleWidget(QWidget):

    def __init__(self, master, from_, to, enabled=True):
        super().__init__(master)

        self._value = from_

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.entry = QLineEdit()
        self.entry.setMaximumWidth(45)
        self.entry.setAlignment(Qt.AlignCenter)
        self.entry.setValidator(QIntValidator(from_, to))
        self.entry.setEnabled(enabled)
        layout.addWidget(self.entry)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(from_)
        self.slider.setMaximum(to)
        self.slider.setMinimumWidth(120)
        self.slider.setEnabled(enabled)
        layout.addWidget(self.slider)

        self.slider.valueChanged.connect(lambda v: self.entry.setText(str(v)))
        self.entry.editingFinished.connect(self._entry_changed)

    def _entry_changed(self):
        try:
            v = int(self.entry.text())
            self.slider.setValue(v)
        except ValueError:
            pass

    def set(self, value):
        self._value = int(value)
        self.slider.setValue(self._value)
        self.entry.setText(str(self._value))

    def get(self):
        try:
            return int(self.entry.text())
        except ValueError:
            return self.slider.value()


class TerrainWidget(QWidget):

    def __init__(self, master):
        super().__init__(master)

        self.cols = 8
        self.terrain_int = 0
        self.options = {}
        self.variables = {}  # index -> bool

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)

        # Read-only terrain integer display
        top_row = QWidget()
        top_layout = QHBoxLayout(top_row)
        top_layout.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel('Terrain Integer')
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.terrain_display = QLineEdit()
        self.terrain_display.setReadOnly(True)
        self.terrain_display.setText('0')
        top_layout.addWidget(lbl)
        top_layout.addWidget(self.terrain_display)
        main_layout.addWidget(top_row)

        self._btn_widget = QWidget()
        self._btn_layout = QGridLayout(self._btn_widget)
        self._btn_layout.setSpacing(2)
        self._btn_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._btn_widget)

        for i, (power, terrain_val, text) in enumerate(TERRAIN_PRIMARY):
            self.variables[i] = False
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.toggled.connect(lambda checked, idx=i: self._on_toggle(idx, checked))
            self.options[i] = btn

        self.update()

    def _on_toggle(self, idx, checked):
        self.variables[idx] = checked
        self._recalculate()

    def _recalculate(self):
        total = 0
        for i, (power, terrain_val, _) in enumerate(TERRAIN_PRIMARY):
            if self.variables.get(i, False):
                total += terrain_val
        self.terrain_int = total
        self.terrain_display.setText(str(total))

    def update(self, cols=None, set_terrain=None):
        if cols is not None:
            self.cols = cols

        if set_terrain is not None:
            for i, (power, terrain_val, _) in enumerate(TERRAIN_PRIMARY):
                checked = has_terrain(set_terrain, terrain_val)
                self.variables[i] = checked
                self.options[i].blockSignals(True)
                self.options[i].setChecked(checked)
                self.options[i].blockSignals(False)
            self.terrain_int = set_terrain
            self.terrain_display.setText(str(set_terrain))

        # Reflow buttons into grid
        for i, btn in self.options.items():
            self._btn_layout.addWidget(btn, i // self.cols, i % self.cols)


class IllwinterDropdownWidget(QWidget):

    def __init__(self, master, data_type, initial_entry=None):
        super().__init__(master)

        options_map = {
            'victory_type'  : ['Victory Conditions', VICTORY_CONDITIONS],
            'poptype'       : ['Poptype', POPTYPES],
            'fort'          : ['Fort', FORT],
            'connection_int': ['Connection type', SPECIAL_NEIGHBOUR],
        }

        text, data = options_map[data_type]
        self.get_dict = {'-': None}
        self.set_dict = {None: '-'}
        entries = ['-']

        for i, j in data:
            entries.append(j)
            self.get_dict[j] = i
            self.set_dict[i] = j

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.setColumnMinimumWidth(0, 100)
        layout.setColumnMinimumWidth(1, 100)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(lbl, 0, 0)

        self.input = QComboBox()
        self.input.addItems(entries)
        layout.addWidget(self.input, 0, 1)

        if initial_entry is not None:
            self.input.setCurrentText(initial_entry)

    def set(self, value):
        self.input.setCurrentText(str(value))

    def get(self):
        return self.get_dict.get(self.input.currentText())


class GeneratorInfoWidget(QWidget):

    def __init__(self, master):
        super().__init__(master)

        self.labels = {}
        self.metrics = {}  # index -> QLineEdit
        self.cols = None

        GENERATOR_INFO = [
            ['Number of provinces', 'text'],
            ['Number of water provinces', 'text'],
            ['Number of cave provinces', 'text'],
            ['Provinces per player', 'text'],
            ['Gold per player', 'text'],
        ]

        main_layout = QGridLayout(self)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setColumnMinimumWidth(0, 150)
        main_layout.setColumnMinimumWidth(1, 200)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 2)

        for i, (text, tooltip) in enumerate(GENERATOR_INFO):
            lbl = QLabel(text)
            lbl.setToolTip(tooltip)
            entry = QLineEdit()
            entry.setAlignment(Qt.AlignCenter)
            entry.setReadOnly(True)
            self.labels[i] = lbl
            self.metrics[i] = entry
            main_layout.addWidget(lbl, i, 0)
            main_layout.addWidget(entry, i, 1)

        # Issues row
        i_last = len(GENERATOR_INFO)
        issues_lbl = QLabel('Input Issues?')
        issues_entry = QLineEdit()
        issues_entry.setReadOnly(True)
        issues_entry.setAlignment(Qt.AlignCenter)
        self.labels[i_last] = issues_lbl
        self.metrics[i_last] = issues_entry
        main_layout.addWidget(issues_lbl, i_last, 0)
        main_layout.addWidget(issues_entry, i_last, 1)

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._check_values)
        self._timer.start()

    def _check_values(self):
        try:
            input_widget = self.parent().parent().parent()
            if not isinstance(input_widget, QtInputWidget):
                return
            settings_dict = input_widget.inputs
        except AttributeError:
            return

        num_players = (
                len(settings_dict['vanilla_nations'].get()) +
                len(settings_dict['custom_nations'].custom_nation_list) +
                len(settings_dict['custom_nations'].generic_nation_list)
        )
        if num_players == 0:
            num_players = 1

        water_provs = (
                settings_dict['water_region_num'].get() *
                REGION_WATER_INFO[WATER_REGIONS.index(settings_dict['water_region_type'].input.currentText())][2] +
                0.05 * num_players *
                settings_dict['periphery_size'].get() *
                settings_dict['player_neighbours'].get()
        )
        cave_provs = (
                settings_dict['cave_region_num'].get() *
                REGION_CAVE_INFO[CAVE_REGIONS.index(settings_dict['cave_region_type'].input.currentText())][2]
        )
        num_provs = (
                num_players * settings_dict['homeland_size'].get() +
                0.5 * num_players * settings_dict['periphery_size'].get() * settings_dict['player_neighbours'].get() +
                settings_dict['throne_region_num'].get() +
                settings_dict['water_region_num'].get() *
                REGION_WATER_INFO[WATER_REGIONS.index(settings_dict['water_region_type'].input.currentText())][2] +
                cave_provs
        )
        provs_per_player = num_provs / num_players
        gold_per_player = (
                300 +
                AGE_POPULATION_MODIFIERS[AGES.index(settings_dict['vanilla_nations'].age.currentText())] *
                100 * num_provs / num_players
        )

        def error_check():
            message = ''
            error = False
            if settings_dict['homeland_size'].get() <= settings_dict['cap_connections'].get():
                message += 'Error: Homeland size must be greater than cap connections  '
                error = True
            if [num_players, settings_dict['player_neighbours'].get()] in NOT_AVAILABLE_GRAPHS:
                message += 'Error: Invalid combination of players and neighbours  '
                error = True
            if num_players > len(DATASET_GRAPHS):
                message += 'Error: Too many players  '
                error = True
            return message if error else "You're good"

        values = [num_provs, water_provs, cave_provs, provs_per_player, gold_per_player, error_check()]
        for i, val in enumerate(values):
            if i in self.metrics:
                self.metrics[i].setText(str(round(val, 2)) if isinstance(val, float) else str(val))
