from .widgets import *
from .loading import *
from .ui_data import *

# UI VARIABLES
########################################################################################################################


class MainInterface(ttk.Frame):

    def __init__(self, master=None):
        self.master = master
        super().__init__()

        self.grid(column=0, row=0, sticky='NEWS')
        self.columnconfigure(0, minsize=380, weight=380)
        self.columnconfigure(1, minsize=1030, weight=1030)
        self.columnconfigure(2, minsize=480, weight=480)
        self.rowconfigure(0, minsize=990, weight=1)

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

        self.editor_focus = None

        self.build_gui()

    def build_gui(self):  # This builds the high level widgets for the UI that are never removed

        # WIDGET FUNCTIONS

        # BUILD UI
        major_frames = list()  # Build 3 major frames
        for frame in range(3):
            major_frames.append(ttk.Frame(self, padding=4))
            major_frames[-1].grid(row=0, column=frame, sticky='NEWS')
            major_frames[-1].grid_rowconfigure(0, weight=1)
            major_frames[-1].grid_columnconfigure(0, weight=1)
        major_frames[2].grid_rowconfigure(0, weight=700, minsize=700)
        major_frames[2].grid_rowconfigure(1, weight=120, minsize=120)
        major_frames[2].grid_rowconfigure(2, weight=80, minsize=80)
        major_frames[2].grid_rowconfigure(3, weight=80, minsize=80)

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
        display_options = ['Show Nodes', 'Show Connections', 'Show Borders', 'Show Capitals', 'Show Thrones', 'Show Armies', 'Enable Wraparound', 'Illwinter Icons']
        display_tags = ['nodes', 'connections', 'borders', 'capitals', 'thrones', 'armies', 'wraparound', 'icons']
        display_states = [1, 1, 1, 0, 0, 0, 0, 0]
        display_styles = ['primary', 'primary', 'primary', 'primary', 'primary', 'primary', 'secondary', 'secondary']
        for i, option in enumerate(display_options):
            variable = ttk.IntVar()
            tag = display_tags[i]
            active = display_states[i]
            iid = ttk.Checkbutton(display_options_frame, bootstyle=display_styles[i], text=option, variable=variable, command=lambda: self.refresh_view(), padding=7, state=ttk.DISABLED)
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
        # self.explorer_panel.tag_bind("explorer_tag", "<<TreeviewSelect>>", item_selected)

        # def do_zoom(event):
        #     x = self.viewing_canvas.canvasx(event.x)
        #     y = self.viewing_canvas.canvasy(event.y)
        #     factor = 1.001 ** event.delta
        #     self.viewing_canvas.scale(ALL, x, y, factor, factor)
        #     # for plane in self.map.planes:
        #     #     for i, iid, bitmap in self.viewing_bitmaps[plane]:
        #     #         iid.zoom(factor)
        #     #     for i, iid, photoimage, trans_photoimage in self.viewing_photoimages[plane]:
        #     #         iid.zoom(factor)

        def right_click(event):
            focus = None
            tag = self.viewing_canvas.find_closest(event.x, event.y)
            if 'clickable' in self.viewing_canvas.gettags(tag):
                if 'nodes' in self.viewing_canvas.gettags(tag):
                    for i, iid in self.viewing_nodes[self.current_plane]:
                        if iid == tag[0]:
                            focus = self.map.province_list[self.current_plane][i-1]
                            break
                elif 'connections' in self.viewing_canvas.gettags(tag):
                    for (i, j), iid in self.viewing_connections[self.current_plane]:
                        if iid == tag[0]:
                            focus = Connection((i, j), 0)
                            break

            self.focus = focus
            self.update_editor_panel()

        # def lense_change(event):
        #     self.selected_lense.set()

        def plane_change(event):
            self.selected_plane.set(int(event.char))
            self.refresh_view()

        self.viewing_canvas.bind("1", plane_change)
        self.viewing_canvas.bind("2", plane_change)
        self.viewing_canvas.bind("3", plane_change)
        self.viewing_canvas.bind("4", plane_change)
        self.viewing_canvas.bind("5", plane_change)
        self.viewing_canvas.bind("6", plane_change)
        self.viewing_canvas.bind("7", plane_change)
        self.viewing_canvas.bind("8", plane_change)
        self.viewing_canvas.bind("9", plane_change)
        # viewing_panel.bind("<w>", v_drag)
        # viewing_panel.bind("<a>", v_drag)
        # viewing_panel.bind("<s>", v_drag)
        # viewing_panel.bind("<d>", v_drag)

        # self.viewing_canvas.bind("<MouseWheel>", do_zoom)  # WINDOWS ONLY
        self.viewing_canvas.bind('<ButtonPress-1>', lambda event: self.viewing_canvas.scan_mark(event.x, event.y))
        self.viewing_canvas.tag_bind('clickable', '<ButtonPress-3>', right_click)
        self.viewing_canvas.bind("<B1-Motion>", lambda event: self.viewing_canvas.scan_dragto(event.x, event.y, gain=1))

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
                    self.explorer_panel.insert(plane_tag, ttk.END, text=f'Province {province.index}', tags="explorer_tag")

            parent = self.explorer_panel.insert("", ttk.END, text="Regions")
            for i, text in enumerate(EXPLORER_REGIONS):
                parent2 = self.explorer_panel.insert(parent, ttk.END, text=text)
                for j, region in enumerate(self.map.region_list[i]):
                    region_tag = self.explorer_panel.insert(parent2, ttk.END, text=f'{region.name}')
                    for province in region.provinces:
                        self.explorer_panel.insert(region_tag, ttk.END, text=f'Province {province.index}', tags="explorer_tag")

    def update_viewing_panel(self):  # This is run whenever the screen needs get updated

        # Need to premake the map layers and set to hidden only using when needed, also draw virtual maps at the other positions and teleport back around when you get to one edge
        if not self.empty:  # If there is data

            self.viewing_bitmaps = [None]*10
            self.bitmap_colors = [None]*10
            self.viewing_photoimages = [None]*10
            self.viewing_connections = [None]*10
            self.viewing_nodes = [None]*10
            self.viewing_borders = [None]*10

            for plane in self.map.planes:  # Create all the PIL objects
                self.viewing_bitmaps[plane] = list()
                self.bitmap_colors[plane] = provinces_2_colours(self.map.province_list[plane])
                self.viewing_connections[plane] = list()
                self.viewing_nodes[plane] = list()
                self.viewing_borders[plane] = list()

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
                image = Image.fromarray(np.flip(pixel_matrix_2_borders_array(self.map.pixel_map[plane], thickness=2).transpose(), axis=0), mode='L')
                border = ImageTk.BitmapImage(image.convert(mode='1', dither=Image.Dither.NONE), foreground='black')
                iid = self.viewing_canvas.create_image(0, 0, anchor=ttk.NW, image=border, state=ttk.HIDDEN, tags=(f'plane{plane}', 'borders'))
                self.viewing_borders[plane] = [iid, border]

                # Making connection objects
                virtual_graph, virtual_coordinates = self.map.layout.province_graphs[plane].get_virtual_graph()
                done_nodes = set()
                for i, (x1, y1) in enumerate(virtual_coordinates):
                    for j in np.argwhere(virtual_graph[i, :] == 1):
                        j = int(j)
                        if j not in done_nodes:
                            x2, y2 = virtual_coordinates[j]
                            iid = self.viewing_canvas.create_line(x1, self.map.map_size[plane][1]-y1, x2, self.map.map_size[plane][1]-y2, state=ttk.HIDDEN, dash=(100, 15), activefill='white', fill='red', tags=(f'plane{plane}', f'{(i+1, j+1)}', 'connections', 'clickable'), width=4)
                            self.viewing_connections[plane].append([(i+1, j+1), iid])
                    colour = 'red'
                    radius = 12
                    width = 3
                    if i >= self.map.layout.province_graphs[plane].size:
                        colour = 'blue'
                        radius = 5
                        width = 2
                    iid = self.viewing_canvas.create_oval(x1-radius, self.map.map_size[plane][1]-(y1-radius), x1+radius, self.map.map_size[plane][1]-(y1+radius), state=ttk.HIDDEN, activefill='white', fill=colour, tags=(f'plane{plane}', f'{i+1}', 'nodes', 'clickable'), width=width)
                    self.viewing_nodes[plane].append([i+1, iid])
                    done_nodes.add(i)

    def update_editor_panel(self):
        if not self.empty:  # If there is data
            if self.focus is not None:  # If there is a focus
                if self.editor_focus is not None:
                    self.editor_focus.destroy()
                if type(self.focus) is Province:
                    self.editor_focus = InputWidget(master=self.editor_frame, ui_config=UI_CONFIG_PROVINCE, cols=1, target_class=self.focus)
                if type(self.focus) is Connection:
                    self.editor_focus = InputWidget(master=self.editor_frame, ui_config=UI_CONFIG_CONNECTION, cols=1, target_class=self.focus)
                self.editor_focus.class_2_input()
                self.editor_focus.grid(row=0, column=0, sticky="NEWS")

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
        InputToplevel(master=self, title='Generate DreamAtlas Map', ui_config=UI_CONFIG_SETTINGS, cols=3, target_class=init_settings, map=self.map)

    def load_map(self, folder):

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

    tools_menu = ttk.Menu(menu, tearoff=0)  # The TOOLS dropdown menu
    # tools_menu.add_command(label="Pixel mapping", command=_config)

    generate_menu = ttk.Menu(menu, tearoff=0)  # The GENERATE dropdown menu
    generate_menu.add_command(label="DreamAtlas", command=lambda: ui.generate_dreamatlas())

    menu.add_cascade(label="File", menu=file_menu)
    menu.add_cascade(label="Tools", menu=tools_menu)
    menu.add_cascade(label="Generators", menu=generate_menu)

    app.mainloop()
