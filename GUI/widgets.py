from DreamAtlas import *
from .loading import GeneratorLoadingWidget
from .ui_data import *


class InputToplevel(ttk.Toplevel):

    def __init__(self, master, title, ui_config, cols, target_type=None, target_class=None, target_location=None, map=None, parent_widget=None):
        super().__init__(title=title, iconphoto=ART_ICON, transient=master, master=master)
        self.columnconfigure(0, weight=1)
        widget = InputWidget(master=self, ui_config=ui_config, cols=cols, target_type=target_type, target_class=target_class, target_location=target_location, map=None, parent_widget=parent_widget)
        widget.grid(row=0, column=0, sticky='NEWS')

        if target_class is not None:
            widget.class_2_input()


class InputWidget(ttk.Frame):

    def __init__(self, master, ui_config, cols, target_type=None, target_class=None, target_location=None, map=None, parent_widget=None):
        super().__init__(master=master)
        self.ui_config = ui_config
        self.cols = cols
        if target_class is None:
            target_class = type(target_type)
        self.target_class = target_class
        self.target_location = target_location
        self.map = map
        self.parent_widget = parent_widget

        self.grid(sticky='NEWS')
        self.grid_columnconfigure(0, weight=1)
        self.labels = dict()
        self.inputs = dict()
        self.variables = dict()
        self.BUTTONS = [
            ['Update', lambda: self.update_class()],
            ['Add', lambda: self.add()],
            ['Generate', lambda: self.generate()],
            ['Save', lambda: self.save()],
            ['Load', lambda: self.load()],
            ['Reset', lambda: self.clear()],
            ['Close', lambda: self.master.destroy()]
        ]
        self.make_gui()

    def make_gui(self):

        frames = list()  # Make the label frames for the inputs and filling them
        for index, (text, attributes) in enumerate(self.ui_config['label_frames']):
            frames.append(ttk.Labelframe(self, text=text, padding=5))
            self.grid_rowconfigure(index, weight=1)
            frames[-1].grid(row=index, column=0, sticky='NEWS', pady=5, padx=10)

            for i, attribute in enumerate(attributes):
                _, widget, label, options, active, tooltip = self.ui_config['attributes'][attribute]

                if widget == 4:
                    self.inputs['vanilla_nations'] = VanillaNationWidget(frames[-1], cols=5)
                elif widget == 5:
                    self.inputs['custom_nations'] = CustomGenericNationWidget(frames[-1], cols=5)
                elif widget == 6:
                    self.inputs[attribute] = IllwinterDropdownWidget(frames[-1], attribute)
                    self.inputs[attribute].grid(row=i, column=0, sticky='NEWS', pady=5, padx=10, rowspan=2)
                elif widget == 7:
                    self.inputs[attribute] = TerrainWidget(frames[-1], cols=4)
                else:
                    state = ttk.NORMAL
                    if not active:
                        state = ttk.DISABLED
                    row, col = i // self.cols, self.cols * (i % self.cols)

                    self.labels[attribute] = ttk.Label(frames[-1], text=label, justify=ttk.CENTER)
                    self.labels[attribute].grid(row=row, column=col, sticky='NEWS', pady=5, padx=5)
                    ToolTip(self.labels[attribute], text=tooltip, delay=750)

                    if widget == 0:
                        self.inputs[attribute] = ttk.Entry(frames[-1], textvariable=ttk.StringVar(), state=state)
                    elif widget == 1:
                        self.inputs[attribute] = ttk.Combobox(frames[-1], values=options, textvariable=ttk.StringVar(), state=ttk.READONLY)
                        self.inputs[attribute].set(options[0])
                    elif widget == 2:
                        self.inputs[attribute] = EntryScaleWidget(frames[-1], variable=ttk.IntVar(), from_=options[0], to=options[1], state=state)
                        self.inputs[attribute].set(options[0])
                    elif widget == 3:
                        self.variables[attribute] = ttk.IntVar()
                        if attribute == 'disciples':
                            self.inputs[attribute] = ttk.Checkbutton(frames[-1], bootstyle="primary-round-toggle", variable=self.variables[attribute], state=state, command=self.update_disciples)
                        else:
                            self.inputs[attribute] = ttk.Checkbutton(frames[-1], bootstyle="primary-round-toggle", variable=self.variables[attribute], state=state)

                    self.inputs[attribute].grid(row=row, column=1+col, sticky='NEWS', pady=5, padx=10)

                ToolTip(self.inputs[attribute], text=tooltip, delay=750)

        if len(self.ui_config['buttons']) > 0:
            button_frame = ttk.Frame(self, bootstyle='primary')
            button_frame.grid(row=len(frames), column=0, sticky='NEWS')

            for index, button in enumerate(self.ui_config['buttons']):
                ttk.Button(button_frame, bootstyle='primary', text=self.BUTTONS[button][0], command=self.BUTTONS[button][1]).grid(row=0, column=index, sticky='WE')
                button_frame.grid_columnconfigure(index, weight=1)

    def update_disciples(self):
        disciples = self.variables['disciples'].get()
        if 'vanilla_nations' in self.inputs:
            self.inputs['vanilla_nations'].update(disciples=disciples)
        if 'custom_nations' in self.inputs:
            self.inputs['custom_nations'].update(disciples=disciples)

    def input_2_class(self):
        for attribute in self.ui_config['attributes']:
            attribute_type, widget, _, options, active, __ = self.ui_config['attributes'][attribute]
            if active:
                if widget == 0:
                    setattr(self.target_class, attribute, attribute_type(self.inputs[attribute].get()))
                if widget == 1:
                    setattr(self.target_class, attribute, attribute_type(options.index(self.inputs[attribute].get())))
                if widget == 2:
                    setattr(self.target_class, attribute, attribute_type(self.inputs[attribute].get()))
                if widget == 3:
                    setattr(self.target_class, attribute, attribute_type(self.variables[attribute].get()))
                elif widget == 4:
                    self.target_class.age = AGES.index(self.inputs[attribute].age.get())
                    self.target_class.vanilla_nations = self.inputs['vanilla_nations'].get()
                elif widget == 5:
                    self.target_class.custom_nations = self.inputs['custom_nations'].custom_nation_list
                    self.target_class.generic_nations = self.inputs['custom_nations'].generic_nation_list
                elif widget == 7:
                    self.target_class.cap_terrain = int(self.inputs['cap_terrain'].terrain_int.get())

    def class_2_input(self):
        for attribute in self.ui_config['attributes']:
            attribute_type, widget, _, options, __, ___ = self.ui_config['attributes'][attribute]

            if getattr(self.target_class, attribute) is not None:
                if widget == 0:
                    self.inputs[attribute].delete(0, END)
                    self.inputs[attribute].insert(1, str(getattr(self.target_class, attribute)))
                elif widget == 1:
                    self.inputs[attribute].set(options[getattr(self.target_class, attribute)])
                elif widget == 2:
                    self.inputs[attribute].set(getattr(self.target_class, attribute))
                elif widget == 3:
                    self.variables[attribute].set(getattr(self.target_class, attribute))
                elif widget == 4:
                    self.inputs[attribute].age.set(AGES[getattr(self.target_class, 'age')])
                    self.inputs[attribute].vanilla_nation_list = getattr(self.target_class, attribute)
                    self.inputs[attribute].update(disciples=getattr(self.target_class, 'disciples'))
                elif widget == 5:
                    self.inputs[attribute].custom_nation_list = getattr(self.target_class, 'custom_nations')
                    self.inputs[attribute].generic_nation_list = getattr(self.target_class, 'generic_nations')
                    self.inputs[attribute].update(disciples=getattr(self.target_class, 'disciples'))

    def input_2_list(self):
        input_list = list()

        for attribute in self.ui_config['attributes']:
            attribute_type, widget, _, options, active = self.ui_config['attributes'][attribute]
            if active:
                if widget == 0:
                    input_list.append(self.inputs[attribute].get())
                if widget == 1:
                    input_list.append(options.index(self.inputs[attribute].get()))
                elif widget == 7:
                    input_list.append(self.inputs['cap_terrain'].terrain_int.get())

        return input_list

    def update_class(self):
        self.input_2_class()

    def add(self):
        self.target_location.append(self.input_2_list())
        self.parent_widget.update()
        self.master.destroy()

    def generate(self):
        self.input_2_class()
        _ = GeneratorLoadingWidget(master=self.master.master, map=self.map, settings=self.target_class)
        _.generate()
        self.master.destroy()

    def save(self):
        self.input_2_class()
        self.target_class.save_file(tkf.asksaveasfilename(parent=self.master, initialdir=ROOT_DIR))

    def load(self):
        self.target_class.load_file(tkf.askopenfilename(parent=self.master, initialdir=ROOT_DIR))
        self.class_2_input()

    def clear(self):
        self.destroy()
        self.__init__(self.master, self.ui_config, self.cols, target_class=self.target_class)
        self.class_2_input()


class VanillaNationWidget(ttk.Frame):

    def __init__(self, master, cols):

        self.master = master
        self.cols = cols
        super().__init__(master=master)
        self.grid(sticky='NEWS')

        self.age = ttk.StringVar()
        self.age.set(AGES[0])

        self.age_selection = ttk.Combobox(self, values=AGES, textvariable=self.age, bootstyle="light", width=7)
        self.age_selection.grid(row=0, column=0, sticky='NEWS', pady=2, padx=2)
        self.age_selection.bind("<<ComboboxSelected>>", lambda x: self.update())

        self.vanilla_nation_list = list()

        self.disciples = 0
        self.options = None
        self.variables = None
        self.miniframes = list()

        self.update()

    def update(self, disciples=None):

        if disciples is not None:
            self.disciples = disciples

        self.options = dict()
        self.variables = dict()

        for frame in self.miniframes:
            for widget in frame.winfo_children():
                widget.destroy()
            frame.destroy()
        self.miniframes.clear()

        age = AGES.index(self.age.get())

        for i, entry in enumerate(AGE_NATIONS[age]):
            self.miniframes.append(ttk.Frame(self))
            self.miniframes[-1].grid(row=1 + i // self.cols, column=i % self.cols, sticky='WE', pady=2, padx=2)

            self.variables[entry[0]] = ttk.IntVar()
            self.options[entry[0]] = ttk.Checkbutton(self.miniframes[-1], text=entry[1], bootstyle="primary-outline-toolbutton", variable=self.variables[entry[0]])
            self.options[entry[0]].grid(row=0, column=0, sticky='WE')

            if self.disciples:
                xj = ttk.Combobox(self.miniframes[-1], values=TEAMS, textvariable=ttk.StringVar(), justify=ttk.CENTER, bootstyle="primary-outline-toolbutton", width=2)
                xj.grid(row=0, column=1, sticky='WE')
                self.miniframes[-1].columnconfigure(1, weight=1, minsize=20)
                xj.set(TEAMS[0])

            for nation, team in self.vanilla_nation_list:
                if entry[0] == nation:
                    self.options[entry[0]].invoke()
                    if self.disciples:
                        xj.set(team)

            self.miniframes[-1].columnconfigure(0, weight=4, minsize=80)

        for i in range(self.cols):
            self.columnconfigure(i, minsize=120)

    def get(self):
        nation_list = list()
        for i, entry in enumerate(AGE_NATIONS[AGES.index(self.age.get())]):

            if self.variables[entry[0]].get():
                nation_list.append([entry[0], 1])
        print(self.age, nation_list)
        return nation_list


class CustomGenericNationWidget(ttk.Frame):

    def __init__(self, master, cols):
        self.master = master
        self.cols = cols
        super().__init__(master=master)
        self.grid(sticky='NEWS')
        self.nation_inputs = dict()
        self.custom_nation_list = list()
        self.generic_nation_list = list()

        self.disciples = 0
        self.miniframes = list()

        add_custom = ttk.Button(self, bootstyle='primary-outline', text='Add Custom Nation', command=lambda: InputToplevel(self, 'Add Custom Nation', UI_CONFIG_CUSTOMNATION, 1, target_location=self.custom_nation_list, parent_widget=self))
        add_custom.grid(row=0, column=0)
        add_generic = ttk.Button(self, bootstyle='primary-outline', text='Add Generic Start', command=lambda: InputToplevel(self, 'Add Generic Start', UI_CONFIG_GENERICNATION, 1, target_location=self.generic_nation_list, parent_widget=self))
        add_generic.grid(row=0, column=1)

        self.update()

    def update(self, disciples=None):

        if disciples is not None:
            self.disciples = disciples

        for frame in self.miniframes:
            for widget in frame.winfo_children():
                widget.destroy()
            frame.destroy()
        self.miniframes.clear()

        bootstyle = ["success", "secondary"]
        for i, nation_list in enumerate([self.custom_nation_list, self.generic_nation_list]):
            for j, nation in enumerate(nation_list):

                count = i * len(self.custom_nation_list) + j
                internal_variable = ttk.IntVar()
                internal_variable.set(j)

                self.miniframes.append(ttk.Frame(self))
                self.miniframes[-1].grid(row=1 + count // self.cols, column=count % self.cols, sticky='WE', pady=2, padx=2)

                if i == 0:
                    text = nation[1]
                else:
                    text = f'Generic Nation {j+1}'

                self.nation_inputs[i] = ttk.Button(self.miniframes[-1], text=text, bootstyle=f'{bootstyle[i]}')
                self.nation_inputs[i].grid(row=0, column=0, sticky='WE')

                plus = 0
                if self.disciples:
                    plus = 1
                    xj = ttk.Combobox(self.miniframes[-1], values=TEAMS, textvariable=ttk.StringVar(), justify=ttk.CENTER, bootstyle=f'outline-toolbutton-{bootstyle[i]}', width=2)
                    xj.grid(row=0, column=1, sticky='WE')
                    xj.set(TEAMS[0])

                if i == 0:
                    xx = ttk.Checkbutton(self.miniframes[-1], text='X', bootstyle=f'outline-toolbutton-{bootstyle[i]}', command=lambda iv=internal_variable: self.remove(self.custom_nation_list, iv))
                else:
                    xx = ttk.Checkbutton(self.miniframes[-1], text='X', bootstyle=f'outline-toolbutton-{bootstyle[i]}', command=lambda iv=internal_variable: self.remove(self.generic_nation_list, iv))
                xx.grid(row=0, column=1+plus, sticky='WE')

                self.miniframes[-1].columnconfigure(0, weight=5, minsize=10)

    def remove(self, nation_list, j):
        nation_list.pop(j.get())
        self.update()


class EntryScaleWidget(ttk.Frame):

    def __init__(self, master, variable, from_, to, state):
        self.master = master
        self.variable = variable
        super().__init__(master=master)
        self.grid()
        self.entry = ttk.Entry(self, state=state, width=3, textvariable=self.variable, justify=ttk.CENTER)
        self.scale = ttk.Scale(self, orient=ttk.HORIZONTAL, variable=variable, from_=from_, to=to, length=140, state=state, command=self.slider_callback)
        self.entry.grid(row=0, column=0, sticky='NEWS', pady=2)
        self.scale.grid(row=0, column=1, sticky='NEWS', padx=5, pady=2)

    def slider_callback(self, event):
        self.variable.set(str(int(float(self.variable.get()))))

    def set(self, i):
        self.variable.set(i)

    def get(self):
        return int(self.variable.get())


class TerrainWidget(ttk.Frame):

    def __init__(self, master, cols):
        self.master = master
        super().__init__(master=master)
        self.grid()

        self.terrain_int = ttk.IntVar()
        ttk.Label(self, text='Terrain Integer').grid(row=0, column=0, sticky='NEWS', pady=5, padx=5)
        ttk.Entry(self, textvariable=self.terrain_int, state=ttk.READONLY).grid(row=0, column=1, sticky='NEWS', pady=5, padx=5)

        self.options = dict()
        self.variables = dict()
        for i, (power, terrain_int, text) in enumerate(TERRAIN_PRIMARY):
            self.variables[i] = ttk.IntVar()
            self.options[i] = ttk.Checkbutton(self, text=text, bootstyle="primary-outline-toolbutton", variable=self.variables[i], command=self.update)
            self.options[i].grid(row=1 + i // cols, column=i % cols, sticky='WE', pady=2, padx=2)

    def update(self):
        terrain_int = 0
        for i, button in enumerate(self.options):
            if self.variables[i].get():
                terrain_int += TERRAIN_PRIMARY[i][1]
        self.terrain_int.set(terrain_int)


class IllwinterDropdownWidget(ttk.Frame):

    def __init__(self, master, data_type):
        self.master = master
        super().__init__(master=master)
        self.grid()

        options = {
            'victory_type': ['Victory Conditions', VICTORY_CONDITIONS],
            'poptype': ['Poptype', POPTYPES],
            'fort': ['Fort', FORT],
            'connection_int': ['Connection type', SPECIAL_NEIGHBOUR]
        }

        text, data = options[data_type]
        entries = [['-']]
        self.get_dict = {'-': None}

        for i, j in data:
            entries.append(j)
            self.get_dict[j] = i

        ttk.Label(self, text=text).grid(row=0, column=0, sticky='NEWS', pady=5, padx=5)

        self.variable = ttk.StringVar()
        self.input = ttk.Combobox(self, values=entries, textvariable=self.variable, state=ttk.READONLY)
        self.input.grid(row=0, column=1, sticky='NEWS', pady=5, padx=5)
        self.input.set(entries[0])

    def get(self):
        return self.get_dict[self.variable]
