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
    QMenuBar, QMenu, QFileDialog, QAbstractItemView, QAction, QShortcut
)
from PyQt5.QtGui import (
    QPixmap, QImage, QColor, QPen, QBrush,
    QKeySequence, QIcon
)
from PyQt5.QtCore import Qt, QRectF, QPointF, pyqtSignal

from .qt_dream_widgets import QtInputWidget, QtInputToplevel
from .qt_ui_data import THEME_FANTASY, INTERFACE_TITLE, INTERFACE_ICON, LENSE_KEY, DISPLAY_OPTIONS, \
    DISPLAY_TAGS, DISPLAY_STATES, EXPLORER_REGIONS, CONNECTION_COLOURS, UI_CONFIG_PROVINCE, UI_CONFIG_CONNECTION, \
    UI_CONFIG_SETTINGS
from ..classes import DominionsMap, DreamAtlasSettings, Province, Connection
from ..databases import ROOT_DIR
from ..functions import has_terrain, provinces_2_colours, pixel_matrix_2_borders_array, pixel_matrix_2_bitmap_arrays


class QtMainInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(INTERFACE_TITLE)
        self.setWindowIcon(QIcon(INTERFACE_ICON))

        self.map = DominionsMap()
        self.settings = DreamAtlasSettings(index=0)

        self.empty = True
        self.focus = None
        self.current_lense = 0
        self.current_plane = 1

        self._selected_lense = 0
        self._selected_plane = 1

        self.display_options = []  # list of (QCheckBox, tag, active)
        self.lense_options = []  # list of QPushButton
        self.plane_options = []  # list of QPushButton
        self._lense_group = QButtonGroup(self)
        self._plane_group = QButtonGroup(self)

        self.editor_focus = None

        self._build_menu()
        self._build_gui()
        self.generate_dreamatlas()

    def _build_menu(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New", self)
        # new_action.triggered.connect(self._action_new)
        file_menu.addAction(new_action)

        save_action = QAction("Save", self)
        # save_action.triggered.connect(self._action_save)
        file_menu.addAction(save_action)

        load_map_action = QAction("Load map", self)
        # load_map_action.triggered.connect(self._action_load_map)
        file_menu.addAction(load_map_action)

        file_menu.addSeparator()

        self._dark_mode_action = QAction("Dark Mode", self)
        self._dark_mode_action.setCheckable(True)
        # self._dark_mode_action.triggered.connect(self._swap_theme)
        file_menu.addAction(self._dark_mode_action)

        # Generators menu
        gen_menu = menubar.addMenu("Generators")
        dreamatlas_action = QAction("DreamAtlas", self)
        dreamatlas_action.triggered.connect(self.generate_dreamatlas)
        gen_menu.addAction(dreamatlas_action)

    def _build_gui(self):

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Create the main layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        root_layout.addWidget(splitter)

        explorer_widget = QWidget()
        splitter.addWidget(explorer_widget)
        viewer_widget = QWidget()
        splitter.addWidget(viewer_widget)
        editor_widget = QWidget()
        splitter.addWidget(editor_widget)
        splitter.setSizes([280, 1090, 520])

        # Explorer setup
        explorer_layout = QVBoxLayout(explorer_widget)
        explorer_layout.setContentsMargins(4, 4, 4, 4)

        explorer_group = QGroupBox("Explorer")
        eg_layout = QVBoxLayout(explorer_group)
        eg_layout.setContentsMargins(2, 8, 2, 2)

        self.explorer_panel = QTreeWidget()
        self.explorer_panel.setHeaderHidden(True)
        self.explorer_panel.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        # self.explorer_panel.itemSelectionChanged.connect(self._on_item_selected)
        eg_layout.addWidget(self.explorer_panel)

        explorer_layout.addWidget(explorer_group)

        # Viewer Setup
        viewer_layout = QVBoxLayout(viewer_widget)
        viewer_layout.setContentsMargins(4, 4, 4, 4)

        viewer_group = QGroupBox("Viewer")
        vg_layout = QVBoxLayout(viewer_group)
        vg_layout.setContentsMargins(3, 8, 3, 3)

        # self.viewing_canvas = MapCanvas()
        # self.viewing_canvas.province_right_clicked.connect(self._on_right_click)
        # vg_layout.addWidget(self.viewing_canvas)

        viewer_layout.addWidget(viewer_group)

        # Editor Setup
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(4, 4, 4, 4)

        # Editor
        self.editor_group = QGroupBox("Editor")
        self.editor_layout = QVBoxLayout(self.editor_group)
        self.editor_layout.setContentsMargins(3, 8, 3, 3)
        self.editor_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Scroll area wrapping editor so it doesn't overflow
        editor_scroll = QScrollArea()
        editor_scroll.setWidgetResizable(True)
        editor_scroll.setWidget(self.editor_group)
        editor_layout.addWidget(editor_scroll, stretch=9)

        # Display options
        display_group = QGroupBox("Display")
        display_grid = QGridLayout(display_group)
        display_grid.setContentsMargins(4, 8, 4, 4)

        for i, option in enumerate(DISPLAY_OPTIONS):
            tag = DISPLAY_TAGS[i]
            active = DISPLAY_STATES[i]
            cb = QCheckBox(option)
            cb.setEnabled(False)
            # cb.stateChanged.connect(self.refresh_view)
            display_grid.addWidget(cb, i // 4, i % 4)
            self.display_options.append((cb, tag, active))

        editor_layout.addWidget(display_group, stretch=1)

        # Lense buttons
        lense_group = QGroupBox("Lense")
        lense_layout = QHBoxLayout(lense_group)
        lense_layout.setContentsMargins(3, 8, 3, 3)
        self._lense_group.setExclusive(True)

        for index, lense in enumerate(['Art', 'Provinces', 'Regions', 'Terrain', 'Population', 'Resources']):
            btn = QPushButton(lense)
            btn.setCheckable(True)
            btn.setEnabled(False)
            btn.setChecked(index == 0)
            self._lense_group.addButton(btn, index)
            lense_layout.addWidget(btn)
            self.lense_options.append(btn)

        # self._lense_group.idClicked.connect(self._on_lense_changed)
        editor_layout.addWidget(lense_group, stretch=1)

        # Plane buttons
        plane_group = QGroupBox("Plane")
        plane_layout = QHBoxLayout(plane_group)
        plane_layout.setContentsMargins(3, 8, 3, 3)
        self._plane_group.setExclusive(True)

        for plane in range(1, 10):
            btn = QPushButton(str(plane))
            btn.setCheckable(True)
            btn.setEnabled(False)
            btn.setChecked(plane == 1)
            self._plane_group.addButton(btn, plane)
            plane_layout.addWidget(btn)
            self.plane_options.append(btn)

        # self._plane_group.idClicked.connect(self._on_plane_changed)
        editor_layout.addWidget(plane_group, stretch=1)

    def update_explorer_panel(self):
        self.explorer_panel.clear()

        if self.empty:
            return

        # Planes branch
        planes_item = QTreeWidgetItem(self.explorer_panel, ["Planes"])
        for plane in self.map.planes:
            plane_item = QTreeWidgetItem(planes_item, [f'Plane {plane}'])
            for province in self.map.province_list[plane]:
                prov_item = QTreeWidgetItem(plane_item, [f'Province {province.plane}-{province.index}'])
                prov_item.setData(0, Qt.ItemDataRole.UserRole, province)

        # Regions branch
        regions_item = QTreeWidgetItem(self.explorer_panel, ["Regions"])
        for i, text in enumerate(EXPLORER_REGIONS):
            cat_item = QTreeWidgetItem(regions_item, [text])
            for region in self.map.region_list[i]:
                region_item = QTreeWidgetItem(cat_item, [region.name])
                for province in region.provinces:
                    prov_item = QTreeWidgetItem(region_item, [f'Province {province.plane}-{province.index}'])
                    prov_item.setData(0, Qt.ItemDataRole.UserRole, province)

        self.explorer_panel.expandToDepth(0)

    def update_viewing_panel(self):
        self.viewing_canvas.clear_scene()

        if self.empty:
            return

        scene = self.viewing_canvas._scene

        for plane in self.map.planes:
            map_h = self.map.map_size[plane][1]

            self.viewing_canvas._bitmaps[plane] = []
            self.viewing_canvas._bitmap_colors[plane] = provinces_2_colours(self.map.province_list[plane])
            self.viewing_canvas._connections[plane] = []
            self.viewing_canvas._nodes[plane] = []
            self.viewing_canvas._icons[plane] = []
            self.viewing_canvas._photoimages[plane] = None

            # --- Province bitmaps ---
            for i, (x, y), array in pixel_matrix_2_bitmap_arrays(self.map.pixel_map[plane]):
                pil_img = Image.fromarray(array, mode='L').convert('RGBA')
                pil_img = pil_img.transpose(Image.Transpose.ROTATE_90)
                px = pil_to_qpixmap(pil_img)
                item = scene.addPixmap(px)
                item.setPos(x, map_h - y)
                item.setVisible(False)
                item.setData(0, i)  # province index
                item.setData(1, plane)  # plane
                item.setData(2, 'bitmap')
                self.viewing_canvas._bitmaps[plane].append((i, item, px))

            # --- Art layer ---
            if self.map.image_file[plane] is not None and self.map.image_file[plane].endswith('.tga'):
                pil_img = Image.open(self.map.image_file[plane])
                px_normal = pil_to_qpixmap(pil_img)
                pil_trans = pil_img.copy();
                pil_trans.putalpha(170)
                px_trans = pil_to_qpixmap(pil_trans)
                art_item = scene.addPixmap(px_normal)
                art_item.setPos(0, 0)
                art_item.setVisible(False)
                art_item.setData(1, plane)
                art_item.setData(2, 'photoimage')
                self.viewing_canvas._photoimages[plane] = (
                    self.map.image_file[plane], art_item, px_normal, px_trans
                )

            # --- Borders ---
            border_arr = pixel_matrix_2_borders_array(self.map.pixel_map[plane], thickness=3)
            border_img = Image.fromarray(np.flip(border_arr.transpose(), axis=0), mode='L').convert('RGBA')
            # Colour black pixels, make white pixels transparent
            r, g, b, a = border_img.split()
            border_img = Image.merge('RGBA', (
                Image.new('L', border_img.size, 0),
                Image.new('L', border_img.size, 0),
                Image.new('L', border_img.size, 0),
                r,  # use luminance channel as alpha mask
            ))
            border_px = pil_to_qpixmap(border_img)
            border_item = scene.addPixmap(border_px)
            border_item.setPos(0, 0)
            border_item.setVisible(False)
            border_item.setData(1, plane)
            border_item.setData(2, 'borders')
            self.viewing_canvas._borders[plane] = (border_item, border_px)

            # Connections & nodes
            virtual_graph, virtual_coordinates = (
                self.map.layout.province_graphs[plane].get_virtual_graph()
            )
            done_nodes = set()
            for i, (x1, y1) in enumerate(virtual_coordinates):
                for j in np.argwhere(virtual_graph[i, :] == 1):
                    j = int(j)
                    colour = CONNECTION_COLOURS[0]
                    for connection in self.map.connection_list[plane]:
                        if {i + 1, j + 1} == connection.connected_provinces:
                            colour = CONNECTION_COLOURS[connection.connection_int]
                            break

                    if j not in done_nodes:
                        x2, y2 = virtual_coordinates[j]
                        pen = QPen(QColor(colour), 6, Qt.PenStyle.DashLine)
                        line = scene.addLine(x1, map_h - y1, x2, map_h - y2, pen)
                        line.setVisible(False)
                        line.setData(0, connection)  # store connection obj for right-click
                        line.setData(1, plane)
                        line.setData(2, 'connections')
                        self.viewing_canvas._connections[plane].append((connection, line))

                if i < self.map.layout.province_graphs[plane].size:
                    ellipse = scene.addEllipse(
                        x1 - 12, map_h - y1 - 12, 24, 24,
                        QPen(Qt.GlobalColor.white, 3),
                        QBrush(Qt.GlobalColor.red)
                    )
                    ellipse.setVisible(False)
                    ellipse.setData(1, plane)
                    ellipse.setData(2, 'nodes')
                    # Store province object for right-click detection
                    if i < len(self.map.province_list[plane]):
                        ellipse.setData(0, self.map.province_list[plane][i])
                    self.viewing_canvas._nodes[plane].append((i + 1, ellipse))
                done_nodes.add(i)

            # --- Icons (thrones, capitals, terrain) ---
            for province in self.map.province_list[plane]:
                x = province.coordinates[0]
                y = map_h - province.coordinates[1]

                if has_terrain(province.terrain_int, 33554432):
                    icon = scene.addPixmap(self.throne_pixmap)
                    icon.setPos(x + 40 - self.throne_pixmap.width() // 2,
                                y - 40 - self.throne_pixmap.height() // 2)
                    icon.setVisible(False)
                    icon.setData(1, plane);
                    icon.setData(2, 'thrones')
                    self.viewing_canvas._icons[plane].append(icon)
                elif has_terrain(province.terrain_int, 67108864):
                    icon = scene.addPixmap(self.capital_pixmap)
                    icon.setPos(x + 30 - self.capital_pixmap.width() // 2,
                                y - 30 - self.capital_pixmap.height() // 2)
                    icon.setVisible(False)
                    icon.setData(1, plane);
                    icon.setData(2, 'capitals')
                    self.viewing_canvas._icons[plane].append(icon)

                for terrain_key in [16, 32, 64, 128, 256, 4, 2052, 132, 4096, 4128, 4160, 4224, 8589934592]:
                    if has_terrain(province.terrain_int, terrain_key):
                        px = self.terrain_pixmaps[terrain_key]
                        icon = scene.addPixmap(px)
                        icon.setPos(x - 30 - px.width() // 2,
                                    y - 40 - px.height() // 2)
                        icon.setVisible(False)
                        icon.setData(1, plane);
                        icon.setData(2, 'terrain')
                        self.viewing_canvas._icons[plane].append(icon)
                        break  # first matching terrain wins, same as original

        # Set scene rect to the largest map
        if self.map.planes:
            max_w = max(self.map.map_size[p][0] for p in self.map.planes)
            max_h = max(self.map.map_size[p][1] for p in self.map.planes)
            self.viewing_canvas._scene.setSceneRect(0, 0, max_w, max_h)

    def update_editor_panel(self):
        # Clear existing editor widget
        if self.editor_focus is not None:
            self.editor_focus.deleteLater()
            self.editor_focus = None

        if self.empty or self.focus is None:
            return

        if isinstance(self.focus, Province):
            self.editor_focus = QtInputWidget(
                master=self.editor_group,
                ui_config=UI_CONFIG_PROVINCE,
                target_class=self.focus
            )
        elif isinstance(self.focus, Connection):
            self.editor_focus = QtInputWidget(
                master=self.editor_group,
                ui_config=UI_CONFIG_CONNECTION,
                target_class=self.focus
            )

        if self.editor_focus is not None:
            self.editor_focus.class_2_input()
            self.editor_layout.addWidget(self.editor_focus)

    def update_plane_lense_panels(self):
        if self.empty:
            return

        for plane in self.map.planes:
            self.plane_options[plane - 1].setEnabled(True)

        for btn in self.lense_options:
            btn.setEnabled(True)

        if self.map.image_file[1] is None:
            self.lense_options[0].setEnabled(False)

        for cb, tag, active in self.display_options:
            if active:
                cb.setEnabled(True)

    def refresh_view(self):
        if self.empty:
            return

        new_plane = self._selected_plane

        # Disable Art lense if no image for this plane
        if self.viewing_canvas._photoimages.get(new_plane) is None:
            self.lense_options[0].setEnabled(False)
            if self._selected_lense == 0:
                self._selected_lense = 1
                btn = self._lense_group.button(1)
                if btn:
                    btn.setChecked(True)

        new_lense = self._selected_lense

        for plane in self.map.planes:
            is_active = (plane == new_plane)

            # Hide all items for inactive planes
            for item in self.viewing_canvas._scene.items():
                if item.data(1) == plane and not is_active:
                    item.setVisible(False)

            if not is_active:
                continue

            art_active = new_lense == 0

            # Update bitmap colours for the selected lense
            if new_lense != self.current_lense or new_plane != self.current_plane:
                for i, item, _px in self.viewing_canvas._bitmaps.get(plane, []):
                    # Recolour: create a tinted copy of the pixmap
                    colour_str = self.viewing_canvas._bitmap_colors[plane][i - 1][new_lense]
                    color = QColor(colour_str)
                    tinted = QPixmap(_px.size())
                    tinted.fill(color)
                    if new_lense != 0:
                        item.setPixmap(tinted)
                        item.setVisible(True)

            # Art layer
            photo_data = self.viewing_canvas._photoimages.get(plane)
            if photo_data is not None:
                _path, art_item, px_normal, px_trans = photo_data
                art_item.setPixmap(px_normal if art_active else px_trans)
                art_item.setVisible(True)

            # Display option toggles
            for cb, tag, active in self.display_options:
                for item in self.viewing_canvas._scene.items():
                    if item.data(1) == plane and item.data(2) == tag:
                        if cb.isChecked():
                            item.setVisible(active)
                        else:
                            item.setVisible(False)

        self.current_plane = new_plane
        self.current_lense = new_lense

    def generate_dreamatlas(self):
        init_settings = DreamAtlasSettings(0)
        init_settings.load_file(ROOT_DIR / 'databases/12_player_ea_test.dream')
        QtInputToplevel(
            master=self,
            title='Generate Map',
            ui_config=UI_CONFIG_SETTINGS,
            target_class=init_settings,
            map=self.map,
        )

    def load_map(self, folder: str):
        if folder:
            self.map.load_folder(folder)
            self.update_gui()

    def load_file(self, file: str):
        self.map.load_file(file)
        self.update_gui()

    def save_map(self, folder: str):
        self.map.publish(folder)

    def _bind_keys(self):

        for plane in range(1, 10):
            sc = QShortcut(QKeySequence(str(plane)), self)
            sc.activated.connect(lambda p=plane: self._on_plane_key(p))

        for char, lense_index in LENSE_KEY.items():
            sc = QShortcut(QKeySequence(char), self)
            sc.activated.connect(lambda li=lense_index: self._on_lense_key(li))

    def _on_plane_key(self, plane: int):
        if plane not in self.map.planes:
            return
        self._selected_plane = plane
        btn = self._plane_group.button(plane)
        if btn:
            btn.setChecked(True)
        self.refresh_view()

    def _on_lense_key(self, lense_index: int):
        self._selected_lense = int(lense_index)
        btn = self._lense_group.button(self._selected_lense)
        if btn:
            btn.setChecked(True)
        self.refresh_view()

    def _on_lense_changed(self, lense_id: int):
        self._selected_lense = lense_id
        self.refresh_view()

    def _on_plane_changed(self, plane_id: int):
        self._selected_plane = plane_id
        self.refresh_view()


def run_qt_interface():
    app = QApplication(sys.argv)
    app.setStyleSheet(THEME_FANTASY)
    app.setWindowIcon(QIcon(INTERFACE_ICON))

    window = QtMainInterface()
    window.showMaximized()
    sys.exit(app.exec())
