from .widgets import *
from .loading import *
from .ui_data import *


class MainInterface(ttk.Frame):

    def __init__(self, master=None):
        super().__init__(master=master)

        self.grid(column=0, row=0, sticky='NEWS')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.map = DominionsMap()
        self.settings = DreamAtlasSettings(index=0)

        self.empty = True
        self.focus = None
        self.view_coordinates = [0, 0]
        self.view_zoom = 1.0

        self.selected_lense = ttk.IntVar()
        self.selected_lense.set(0)
        self.current_lense = 0

        self.selected_plane = ttk.IntVar()
        self.selected_plane.set(1)
        self.current_plane = 1

        self.display_options = list()
        self.lense_options = list()
        self.plane_options = list()

        self.viewing_bitmaps = None
        self.bitmap_colors = None
        self.viewing_photoimages = None
        self.viewing_connections = None
        self.viewing_nodes = None
        self.viewing_borders = None
        self.icons = None

        self.editor_focus = None

        self.throne_image = ImageTk.PhotoImage(Image.open(ROOT_DIR / 'databases/ui_images/throne.png'))
        self.capital_image = ImageTk.PhotoImage(Image.open(ROOT_DIR / 'databases/ui_images/capital.png'))
        self.terrain_images = {16: ImageTk.PhotoImage(Image.open(ROOT_DIR / 'databases/ui_images/highland.png')),
                               32: ImageTk.PhotoImage(Image.open(ROOT_DIR / 'databases/ui_images/swamp.png')),
                               64: ImageTk.PhotoImage(Image.open(ROOT_DIR / 'databases/ui_images/waste.png')),
                               128: ImageTk.PhotoImage(Image.open(ROOT_DIR / 'databases/ui_images/forest.png')),
                               256: ImageTk.PhotoImage(Image.open(ROOT_DIR / 'databases/ui_images/farm.png')),
                               4: ImageTk.PhotoImage(Image.open(ROOT_DIR / 'databases/ui_images/sea.png')),
                               2052: ImageTk.PhotoImage(Image.open(ROOT_DIR / 'databases/ui_images/deep.png')),
                               132: ImageTk.PhotoImage(Image.open(ROOT_DIR / 'databases/ui_images/kelp.png')),
                               4096: ImageTk.PhotoImage(Image.open(ROOT_DIR / 'databases/ui_images/cave.png')),
                               4128: ImageTk.PhotoImage(Image.open(ROOT_DIR / 'databases/ui_images/drip.png')),
                               4160: ImageTk.PhotoImage(Image.open(ROOT_DIR / 'databases/ui_images/crystal.png')),
                               4224: ImageTk.PhotoImage(Image.open(ROOT_DIR / 'databases/ui_images/mushroom.png')),
                               8589934592: ImageTk.PhotoImage(Image.open(ROOT_DIR / 'databases/ui_images/vast.png'))
        }

        self.build_gui()

    def build_gui(self):  # This builds the high level widgets for the UI that are never removed

        # WIDGET FUNCTIONS
        # BUILD UI
        major_pane = ttk.PanedWindow(self, orient=ttk.HORIZONTAL)
        major_pane.grid(row=0, column=0, sticky='NEWS')

        major_frames = list()  # Build 3 major frames
        weights = [280, 1090, 520]
        for frame in range(3):
            major_frames.append(ttk.Frame(major_pane, padding=4))
            major_pane.add(major_frames[-1], weight=weights[frame])
            major_frames[-1].grid_rowconfigure(0, weight=1)
            major_frames[-1].grid_columnconfigure(0, weight=1)
        major_frames[2].grid_rowconfigure(0, weight=900)
        major_frames[2].grid_rowconfigure(1, weight=120)
        major_frames[2].grid_rowconfigure(2, weight=80)
        major_frames[2].grid_rowconfigure(3, weight=80)

        # Object explorer_panel lets you view and select all the objects in the map
        explorer_frame = ttk.Labelframe(major_frames[0], text="Explorer", padding=2)
        explorer_frame.grid(row=0, column=0, sticky='NEWS')
        explorer_frame.grid_columnconfigure(0, weight=100)
        explorer_frame.grid_columnconfigure(1, weight=1)
        explorer_frame.grid_rowconfigure(0, weight=1)

        self.explorer_panel = ttk.Treeview(explorer_frame, bootstyle="default", show="tree")
        explorer_scrollbar = ttk.Scrollbar(explorer_frame, bootstyle="primary", orient='vertical', command=self.explorer_panel.yview)
        self.explorer_panel['yscrollcommand'] = explorer_scrollbar.set
        self.explorer_panel.grid(row=0, column=0, sticky='NEWS')
        explorer_scrollbar.grid(row=0, column=1, sticky='NEWS')

        # Making the map viewing/editing window
        viewing_frame = ttk.Labelframe(major_frames[1], text="Viewer", padding=3)
        viewing_frame.grid(row=0, column=0, sticky='NEWS')
        viewing_frame.grid_rowconfigure(0, weight=100)
        viewing_frame.grid_columnconfigure(0, weight=100)
        self.viewing_canvas = ttk.Canvas(viewing_frame, takefocus=True, confine=False, )
        self.viewing_canvas.grid(row=0, column=0, sticky='NEWS')

        # Making the province editing panel
        self.editor_frame = ttk.Labelframe(major_frames[2], text="Editor", padding=3)
        self.editor_frame.grid(row=0, column=0, sticky='NEWS')
        self.editor_frame.grid_columnconfigure(0, weight=1)

        # Making the display options buttons
        display_options_frame = ttk.Labelframe(major_frames[2], text="Display", padding=4)
        display_options_frame.grid(row=1, column=0, sticky='NEWS')
        for i, option in enumerate(DISPLAY_OPTIONS):
            variable = ttk.IntVar()
            tag = DISPLAY_TAGS[i]
            active = DISPLAY_STATES[i]
            iid = ttk.Checkbutton(display_options_frame, bootstyle=DISPLAY_STYLES[i], text=option, variable=variable, command=lambda: self.refresh_view(), padding=7, state=ttk.DISABLED)
            iid.grid(row=i//4, column=i % 4, sticky='NEWS')
            self.display_options.append([variable, tag, active, iid])

        # Making the map lense buttons
        lense_button_frame = ttk.Labelframe(major_frames[2], text="Lense", padding=3)
        lense_button_frame.grid(row=2, column=0, sticky='NEWS')
        lense_button_frame.grid_rowconfigure(0, weight=1)
        for index, lense in enumerate(['Art', 'Provinces', 'Regions', 'Terrain', 'Population', 'Resources']):
            iid = ttk.Radiobutton(lense_button_frame, bootstyle="primary-outline-toolbutton", text=lense, variable=self.selected_lense, command=lambda: self.refresh_view(), value=index, state=ttk.DISABLED)
            iid.grid(row=0, column=index, sticky='NEWS')
            lense_button_frame.grid_columnconfigure(index, weight=1)
            self.lense_options.append(iid)

        # Making the plane selection buttons
        plane_button_frame = ttk.Labelframe(major_frames[2], text="Plane", padding=3)
        plane_button_frame.grid(row=3, column=0, sticky='NEWS')
        plane_button_frame.grid_rowconfigure(0, weight=1)

        for plane in range(1, 10):
            iid = ttk.Radiobutton(plane_button_frame, bootstyle='primary-outline-toolbutton', text=str(plane), variable=self.selected_plane, command=lambda: self.refresh_view(), value=plane, state=ttk.DISABLED)
            iid.grid(row=0, column=plane-1, sticky='NEWS')
            plane_button_frame.grid_columnconfigure(plane-1, weight=1)
            self.plane_options.append(iid)

        # BINDINGS

        def item_selected(event):  # Update the focus based on the selected item
            selected_item = self.explorer_panel.selection()
            if selected_item:
                item_id = selected_item[0]

                for plane in self.map.planes:
                    for province in self.map.province_list[plane]:
                        if f'Province {province.plane}-{province.index}' == self.explorer_panel.item(item_id, 'text'):
                            self.focus = province
                            self.update_editor_panel()
                            self.selected_plane.set(int(plane))
                            self.viewing_canvas.xview_moveto(province.coordinates[0] / self.map.map_size[plane][0])
                            self.viewing_canvas.yview_moveto(province.coordinates[1] / self.map.map_size[plane][1])
                            self.refresh_view()
                            return

        def right_click(event):

            tag = self.viewing_canvas.find_closest(self.viewing_canvas.canvasx(event.x), self.viewing_canvas.canvasy(event.y))
            if 'clickable' in self.viewing_canvas.gettags(tag):
                if 'nodes' in self.viewing_canvas.gettags(tag):
                    for i, iid in self.viewing_nodes[self.current_plane]:
                        if iid == tag[0]:
                            self.focus = self.map.province_list[self.current_plane][i-1]
                            break
                elif 'connections' in self.viewing_canvas.gettags(tag):
                    for connection, iid in self.viewing_connections[self.current_plane]:
                        if iid == tag[0]:
                            self.focus = connection
                            break

            self.update_editor_panel()

        def plane_change(event):
            if int(event.char) not in self.map.planes:
                return
            self.selected_plane.set(int(event.char))
            self.refresh_view()

        def lense_change(event):
            self.selected_lense.set(int(LENSE_KEY[event.char]))
            self.refresh_view()

        self.explorer_panel.tag_bind("explorer_tag", "<<TreeviewSelect>>", item_selected)

        self.master.bind("1", plane_change)
        self.master.bind("2", plane_change)
        self.master.bind("3", plane_change)
        self.master.bind("4", plane_change)
        self.master.bind("5", plane_change)
        self.master.bind("6", plane_change)
        self.master.bind("7", plane_change)
        self.master.bind("8", plane_change)
        self.master.bind("9", plane_change)

        self.master.bind("z", lense_change)
        self.master.bind("x", lense_change)
        self.master.bind("c", lense_change)
        self.master.bind("v", lense_change)
        self.master.bind("b", lense_change)
        self.master.bind("n", lense_change)

        # self.viewing_canvas.bind("<MouseWheel>", do_zoom)  # WINDOWS ONLY
        self.viewing_canvas.bind('<ButtonPress-1>', lambda event: self.viewing_canvas.scan_mark(event.x, event.y))
        self.viewing_canvas.bind("<B1-Motion>", lambda event: self.viewing_canvas.scan_dragto(event.x, event.y, gain=1))
        self.viewing_canvas.tag_bind('clickable', '<ButtonPress-3>', right_click)

    def update_gui(self):
        self.empty = False
        self.update_explorer_panel()
        self.update_viewing_panel()
        self.update_editor_panel()
        self.update_plane_lense_panels()
        self.refresh_view()

    # UPDATE FUNCTIONS
    def update_explorer_panel(self):

        for i in self.explorer_panel.winfo_children():
            i.destroy()

        if not self.empty:  # If there is data
            parent = self.explorer_panel.insert("", ttk.END, text="Planes")
            for plane in self.map.planes:
                plane_tag = self.explorer_panel.insert(parent, ttk.END, text=f'Plane {plane}')
                for province in self.map.province_list[plane]:
                    self.explorer_panel.insert(plane_tag, ttk.END, text=f'Province {province.plane}-{province.index}', tags="explorer_tag")

            parent = self.explorer_panel.insert("", ttk.END, text="Regions")
            for i, text in enumerate(EXPLORER_REGIONS):
                parent2 = self.explorer_panel.insert(parent, ttk.END, text=text)
                for j, region in enumerate(self.map.region_list[i]):
                    region_tag = self.explorer_panel.insert(parent2, ttk.END, text=f'{region.name}')
                    for province in region.provinces:
                        self.explorer_panel.insert(region_tag, ttk.END, text=f'Province {province.plane}-{province.index}', tags="explorer_tag")

    def update_viewing_panel(self):  # This is run whenever the screen needs get updated

        for i in self.viewing_canvas.winfo_children():
            i.destroy()

        # Need to premake the map layers and set to hidden only using when needed, also draw virtual maps at the other positions and teleport back around when you get to one edge
        if not self.empty:  # If there is data

            self.viewing_bitmaps = [None]*10
            self.bitmap_colors = [None]*10
            self.viewing_photoimages = [None]*10
            self.viewing_connections = [None]*10
            self.viewing_nodes = [None]*10
            self.viewing_borders = [None]*10
            self.icons = [None]*10

            for plane in self.map.planes:  # Create all the PIL objects
                self.viewing_bitmaps[plane] = list()
                self.bitmap_colors[plane] = provinces_2_colours(self.map.province_list[plane])
                self.viewing_connections[plane] = list()
                self.viewing_nodes[plane] = list()
                self.viewing_borders[plane] = list()
                self.icons[plane] = list()

                # Making province border objects (useful for a lot of stuff)
                for i, (x, y), array in pixel_matrix_2_bitmap_arrays(self.map.pixel_map[plane]):  # Iterating through every province index on this pixel map
                    image = Image.fromarray(array, mode='L').convert(mode='1', dither=Image.Dither.NONE)
                    image = image.transpose(method=Image.Transpose.ROTATE_90)
                    bitmap = ImageTk.BitmapImage(image)
                    iid = self.viewing_canvas.create_image(x, self.map.map_size[plane][1]-y, anchor=ttk.SW, image=bitmap, state=ttk.HIDDEN, tags=(f'plane{plane}', f'{i}', 'bitmap'))
                    self.viewing_bitmaps[plane].append([i, iid, bitmap])

                # Making art objects
                if self.map.image_file[plane] is not None:
                    if self.map.image_file[plane].endswith('.tga'):  # Art layer
                        image = Image.open(self.map.image_file[plane])
                        photoimage = ImageTk.PhotoImage(image)
                        image2 = image.copy()
                        image2.putalpha(170)
                        trans_photoimage = ImageTk.PhotoImage(image2)
                        iid = self.viewing_canvas.create_image(0, 0, anchor=ttk.NW, image=photoimage, disabledimage=trans_photoimage, state=ttk.HIDDEN, tags=(f'plane{plane}', 'photoimage'))
                        self.viewing_photoimages[plane] = [self.map.image_file[plane], iid, photoimage, trans_photoimage]

                # Making borders
                image = Image.fromarray(np.flip(pixel_matrix_2_borders_array(self.map.pixel_map[plane], thickness=3).transpose(), axis=0), mode='L')
                border = ImageTk.BitmapImage(image.convert(mode='1', dither=Image.Dither.NONE), foreground='black')
                iid = self.viewing_canvas.create_image(0, 0, anchor=ttk.NW, image=border, state=ttk.HIDDEN, tags=(f'plane{plane}', 'borders'))
                self.viewing_borders[plane] = [iid, border]

                # Making connection objects
                virtual_graph, virtual_coordinates = self.map.layout.province_graphs[plane].get_virtual_graph()
                done_nodes = set()
                for i, (x1, y1) in enumerate(virtual_coordinates):
                    for j in np.argwhere(virtual_graph[i, :] == 1):
                        j = int(j)

                        neighbour_col = CONNECTION_COLOURS[0]
                        for connection in self.map.connection_list[plane]:
                            if {i+1, j+1} == connection.connected_provinces:
                                neighbour_col = CONNECTION_COLOURS[connection.connection_int]
                                break

                        if j not in done_nodes:
                            x2, y2 = virtual_coordinates[j]
                            iid = self.viewing_canvas.create_line(x1, self.map.map_size[plane][1]-y1, x2, self.map.map_size[plane][1]-y2, state=ttk.HIDDEN, dash=(100, 15), activefill='white', fill=neighbour_col, tags=(f'plane{plane}', f'{(i+1, j+1)}', 'connections', 'clickable'), width=6)
                            self.viewing_connections[plane].append([connection, iid])

                    if i < self.map.layout.province_graphs[plane].size:
                        iid = self.viewing_canvas.create_oval(x1-12, self.map.map_size[plane][1]-(y1-12), x1+12, self.map.map_size[plane][1]-(y1+12), state=ttk.HIDDEN, activefill='white', fill='red', tags=(f'plane{plane}', f'{i+1}', 'nodes', 'clickable'), width=3)
                        self.viewing_nodes[plane].append([i+1, iid])
                    done_nodes.add(i)

                # Making image layers
                for province in self.map.province_list[plane]:
                    x = province.coordinates[0]
                    y = self.map.map_size[plane][1] - province.coordinates[1]
                    if has_terrain(province.terrain_int, 33554432):
                        iid = self.viewing_canvas.create_image(x+40, y-40, anchor=ttk.CENTER, image=self.throne_image, state=ttk.HIDDEN, tags=(f'plane{plane}', 'thrones'))
                        self.icons[plane].append(iid)
                    elif has_terrain(province.terrain_int, 67108864):
                        iid = self.viewing_canvas.create_image(x+30, y-30, anchor=ttk.CENTER, image=self.capital_image, state=ttk.HIDDEN, tags=(f'plane{plane}', 'capitals'))
                        self.icons[plane].append(iid)  # Store the icons for later use

                    image = None
                    for terrain in [16, 32, 64, 128, 256, 4, 2052, 132, 4096, 4128, 4160, 4224, 8589934592]:  # Check for terrain types
                        if has_terrain(province.terrain_int, terrain):
                            image = self.terrain_images[terrain]
                    if image is not None:
                        iid = self.viewing_canvas.create_image(x-30, y-40, anchor=ttk.CENTER, image=image, state=ttk.HIDDEN, tags=(f'plane{plane}', 'info', 'terrain'))
                        self.icons[plane].append(iid)  # Store the icons for later use

    def update_editor_panel(self):

        for i in self.editor_frame.winfo_children():
            i.destroy()

        if not self.empty:  # If there is data
            if self.focus is not None:  # If there is a focus
                if self.editor_focus is not None:
                    self.editor_focus.destroy()
                if type(self.focus) is Province:
                    self.editor_focus = InputWidget(master=self.editor_frame, ui_config=UI_CONFIG_PROVINCE, target_class=self.focus)
                elif type(self.focus) is Connection:
                    self.editor_focus = InputWidget(master=self.editor_frame, ui_config=UI_CONFIG_CONNECTION, target_class=self.focus)
                self.editor_focus.class_2_input()
                self.editor_focus.pack(fill=BOTH, expand=True, side=TOP)
                self.editor_focus.make_size(1)

    def update_plane_lense_panels(self):
        if not self.empty:
            for plane in self.map.planes:
                self.plane_options[plane-1].config(state=ttk.NORMAL)

            for iid in self.lense_options:
                iid.config(state=ttk.NORMAL)

            if self.map.image_file[1] is None:
                self.lense_options[0].config(state=ttk.DISABLED)

            for variable, tag, active, iid in self.display_options:
                if active:
                    iid.config(state=ttk.NORMAL)

    def refresh_view(self):  # This function handles switching the views and updating the viewer images
        if not self.empty:  # If there is data

            new_plane = self.selected_plane.get()

            if self.viewing_photoimages[new_plane] is None:
                self.lense_options[0].config(state=ttk.DISABLED)
                if self.selected_lense.get() == 0:
                    self.selected_lense.set(1)

            new_lense = self.selected_lense.get()

            self.viewing_canvas.config(confine=True, scrollregion=(0, 0, self.map.map_size[new_plane][0], self.map.map_size[new_plane][1]))

            for plane in self.map.planes:

                if plane != new_plane:
                    self.viewing_canvas.itemconfigure(f'plane{plane}', state=ttk.HIDDEN)
                else:
                    art_active = 0
                    if new_lense == 0:
                        art_active = 1
                    elif new_lense != self.current_lense or new_plane != self.current_plane:
                        for i, iid, bitmap in self.viewing_bitmaps[plane]:  # Update the province bitmap colours
                            colour = self.bitmap_colors[plane][i-1][new_lense]
                            bitmap._BitmapImage__photo.config(foreground=colour)
                            if new_lense != 0:
                                self.viewing_canvas.itemconfigure(f'plane{plane}', state=ttk.NORMAL)

                    if self.viewing_photoimages[plane] is not None:
                        i, iid, photoimage, trans_photoimage = self.viewing_photoimages[plane]
                        self.viewing_canvas.itemconfigure(iid, state=UI_STATES[art_active])  # Update the art layer

                    for variable, tag, active, _ in self.display_options:  # Update the display options
                        self.viewing_canvas.itemconfigure(tag, state=ttk.HIDDEN)
                        if variable.get():
                            for iid in self.viewing_canvas.find_withtag(tag):
                                if f'plane{plane}' in self.viewing_canvas.gettags(iid):
                                    self.viewing_canvas.itemconfigure(iid, state=UI_STATES[active])

            self.current_plane = new_plane
            self.current_lense = new_lense

    def generate_dreamatlas(self):

        init_settings = DreamAtlasSettings(0)
        init_settings.load_file(ROOT_DIR / 'databases/12_player_ea_test.dream')
        InputToplevel(master=self, title='Generate DreamAtlas Map', ui_config=UI_CONFIG_SETTINGS, target_class=init_settings, map=self.map, geometry="900x600")

    def load_map(self, folder):
        if folder != '':
            self.map.load_folder(folder)
            self.update_gui()

    def load_file(self, file):
        self.map.load_file(file)
        self.update_gui()

    def save_map(self, folder):
        self.map.publish(folder)


def run_interface():
    app = ttk.Window(title="DreamAtlas", themename='dreamfantasy', iconphoto=ART_ICON)
    app.place_window_center()
    app.rowconfigure(0, weight=1)
    app.columnconfigure(0, weight=1)
    app.state('zoomed')

    def _config():
        x = 1

    style_button = ttk.IntVar()

    def swap_theme():
        if style_button.get():
            app.style.theme_use('dreamvampire')
        else:
            app.style.theme_use('dreamfantasy')

    ui = MainInterface(app)

    menu = ttk.Menu(app)
    app.config(menu=menu)
    file_menu = ttk.Menu(menu, tearoff=0)  # The FILE dropdown menu
    file_menu.add_command(label="New", command=lambda: [ui.destroy(), ui.__init__(app)])
    file_menu.add_command(label="Save", command=lambda: ui.save_map(tkf.asksaveasfilename(parent=app, initialdir=LOAD_DIR, initialfile=ui.map.map_title)))
    file_menu.add_command(label="Load map", command=lambda: ui.load_map(tkf.askdirectory(parent=app, initialdir=LOAD_DIR)))
    # file_menu.add_command(label="Load file", command=lambda: ui.load_file(tkf.askopenfilename(parent=app, initialdir=ROOT_DIR.parent)))
    # file_menu.add_separator()
    # file_menu.add_command(label="Settings", command=_config)
    file_menu.add_separator()
    file_menu.add_checkbutton(label="Dark Mode", command=lambda: swap_theme(), variable=style_button)  # The HELP button

    # tools_menu = ttk.Menu(menu, tearoff=0)  # The TOOLS dropdown menu
    # tools_menu.add_command(label="Convert to .d6m", command=lambda: ui.map.convert_to_d6m())

    generate_menu = ttk.Menu(menu, tearoff=0)  # The GENERATE dropdown menu
    generate_menu.add_command(label="DreamAtlas", command=lambda: ui.generate_dreamatlas())

    menu.add_cascade(label="File", menu=file_menu)
    # menu.add_cascade(label="Tools", menu=tools_menu)
    menu.add_cascade(label="Generators", menu=generate_menu)

    app.mainloop()
