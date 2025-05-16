from DreamAtlas import *
from .loading import GeneratorLoadingWidget
from .ui_data import *


class InputToplevel(ttk.Toplevel):

    def __init__(self, master, title, ui_config, target_type=None, target_class=None, target_location=None, map=None, parent_widget=None):
        super().__init__(title=title, iconphoto=ART_ICON, transient=master, master=master)
        widget = InputWidget(master=self, ui_config=ui_config, target_type=target_type, target_class=target_class, target_location=target_location, map=None, parent_widget=parent_widget)
        widget.pack(fill=BOTH, expand=True)
        self.geometry("")

        if target_class is not None:
            widget.class_2_input()


class InputWidget(ttk.Frame):

    def __init__(self, master, ui_config,target_type=None, target_class=None, target_location=None, map=None, parent_widget=None):
        super().__init__(master=master)
        self.ui_config = ui_config
        if target_class is None:
            target_class = type(target_type)
        self.target_class = target_class
        self.target_location = target_location
        self.map = map
        self.parent_widget = parent_widget

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

        wrap_frame = ttk.Text(self, state=ttk.DISABLED)
        scrollbar = ttk.Scrollbar(self, bootstyle="primary", orient='vertical', command=wrap_frame.yview)
        wrap_frame.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(fill=Y, side=RIGHT)
        wrap_frame.pack(fill=BOTH, expand=True, side=TOP, anchor=NW)

        base_frame = ttk.Frame(self)
        wrap_frame.window_create(window=base_frame, index='end', align=TOP)

        frames = list()  # Make the label frames for the inputs and filling them
        for index, (text, attributes) in enumerate(self.ui_config['label_frames']):
            frames.append(ttk.Labelframe(base_frame, text=text, padding=5))
            frames[-1].pack(fill=BOTH, expand=True, side=TOP, padx=5, pady=2)

            for i, attribute in enumerate(attributes):
                if attribute == 'generation_info':
                    self.info = GeneratorInfoWidget(frames[-1])
                    self.info.pack(fill=X, expand=True, side=RIGHT)
                    break
                _, widget, label, options, active, tooltip = self.ui_config['attributes'][attribute]

                if widget == 4:
                    self.inputs['vanilla_nations'] = VanillaNationWidget(frames[-1])
                elif widget == 5:
                    self.inputs['custom_nations'] = CustomGenericNationWidget(frames[-1])
                elif widget == 6:
                    self.inputs[attribute] = IllwinterDropdownWidget(frames[-1], attribute)
                    self.inputs[attribute].pack(fill=X, expand=False, side='left')
                elif widget == 7:
                    self.inputs[attribute] = TerrainWidget(frames[-1])
                else:
                    state = ttk.NORMAL
                    if not active:
                        state = ttk.DISABLED

                    miniframe = ttk.Frame(frames[-1])
                    miniframe.pack(fill=X, expand=False, side=TOP, padx=2, pady=2)

                    self.labels[attribute] = ttk.Label(miniframe, text=label, justify=ttk.CENTER)
                    self.labels[attribute].pack(fill='both', expand=False, side=LEFT)
                    ToolTip(self.labels[attribute], text=tooltip, delay=TOOLTIP_DELAY)

                    if widget == 0:
                        self.inputs[attribute] = ttk.Entry(miniframe, textvariable=ttk.StringVar(), state=state)
                    elif widget == 1:
                        self.inputs[attribute] = ttk.Combobox(miniframe, values=options, textvariable=ttk.StringVar(), state=ttk.READONLY)
                        self.inputs[attribute].set(options[0])
                    elif widget == 2:
                        self.inputs[attribute] = EntryScaleWidget(miniframe, variable=ttk.IntVar(), from_=options[0], to=options[1], state=state)
                        self.inputs[attribute].set(options[0])
                    elif widget == 3:
                        self.variables[attribute] = ttk.IntVar()
                        if attribute == 'disciples':
                            self.inputs[attribute] = ttk.Checkbutton(miniframe, bootstyle="primary-round-toggle", variable=self.variables[attribute], state=state, command=self.update_disciples)
                        else:
                            self.inputs[attribute] = ttk.Checkbutton(miniframe, bootstyle="primary-round-toggle", variable=self.variables[attribute], state=state)

                self.inputs[attribute].pack(fill=X, expand=False, side=RIGHT)

                ToolTip(self.inputs[attribute], text=tooltip, delay=TOOLTIP_DELAY)

        if len(self.ui_config['buttons']) > 0:
            button_frame = ttk.Frame(self, bootstyle='primary')
            button_frame.pack(fill=X, expand=False, side=BOTTOM, anchor=SW)

            for index, button in enumerate(self.ui_config['buttons']):
                ttk.Button(button_frame, bootstyle='primary', text=self.BUTTONS[button][0], command=self.BUTTONS[button][1]).pack(fill=X, expand=True, side='left')

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
            attribute_type, widget, _, options, active, __ = self.ui_config['attributes'][attribute]
            if active:
                if widget == 0:
                    input_list.append(self.inputs[attribute].get())
                if widget == 1:
                    if attribute == 'home_plane':
                        input_list.append(1+options.index(self.inputs[attribute].get()))
                    else:
                        input_list.append(options.index(self.inputs[attribute].get()))
                elif widget == 7:
                    input_list.append(self.inputs['terrain'].terrain_int.get())

        input_list.append(1)  # Temporary fix for teams

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
        self.target_class.save_file(tkf.asksaveasfilename(parent=self.master, initialdir=LOAD_DIR))

    def load(self):
        self.target_class.load_file(tkf.askopenfilename(parent=self.master, initialdir=LOAD_DIR))
        self.class_2_input()

    def clear(self):
        self.destroy()
        self.__init__(self.master, self.ui_config, target_class=self.target_class)
        self.class_2_input()


class VanillaNationWidget(ttk.Frame):

    def __init__(self, master):

        self.master = master
        super().__init__(master=master)

        self.age = ttk.StringVar()
        self.age.set(AGES[0])

        self.age_selection = ttk.Combobox(self, values=AGES, textvariable=self.age, bootstyle="light", width=7)
        self.age_selection.pack(fill=X, expand=False, side=TOP)
        self.age_selection.bind("<<ComboboxSelected>>", lambda x: self.update())

        self.vanilla_nation_list = list()

        self.disciples = 0
        self.options = None
        self.variables = None
        self.miniframes = list()
        self.wrap_frame = ttk.Text(self, state=ttk.DISABLED, width=50, height=10)
        self.wrap_frame.pack(fill=X, expand=False, side=TOP, anchor=NW)

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
            new_frame = ttk.Frame(self)
            self.wrap_frame.window_create(window=new_frame, index='end')
            self.miniframes.append(new_frame)
            # self.miniframes[-1].pack(fill=X, expand=False, side='left')

            self.variables[entry[0]] = ttk.IntVar()
            self.options[entry[0]] = ttk.Checkbutton(self.miniframes[-1], text=entry[1], bootstyle="primary-outline-toolbutton", variable=self.variables[entry[0]])
            self.options[entry[0]].pack(fill=X, expand=False, side='left')

            if self.disciples:
                xj = ttk.Combobox(self.miniframes[-1], values=TEAMS, textvariable=ttk.StringVar(), justify=ttk.CENTER, bootstyle="primary-outline-toolbutton", width=2)
                xj.pack(fill=X, expand=False, side='left')
                xj.set(TEAMS[0])

            for nation, team in self.vanilla_nation_list:
                if entry[0] == nation:
                    self.options[entry[0]].invoke()
                    if self.disciples:
                        xj.set(team)

    def get(self):
        nation_list = list()
        for i, entry in enumerate(AGE_NATIONS[AGES.index(self.age.get())]):

            if self.variables[entry[0]].get():
                nation_list.append([entry[0], 1])
        return nation_list


class CustomGenericNationWidget(ttk.Frame):

    def __init__(self, master):
        super().__init__(master=master)
        self.nation_inputs = dict()
        self.custom_nation_list = list()
        self.generic_nation_list = list()

        self.disciples = 0
        self.miniframes = list()

        self.wrap_frame = ttk.Text(self, state=ttk.DISABLED, width=50, height=10)
        self.wrap_frame.pack(fill=X, expand=False, side=TOP, anchor=NW)

        add_custom = ttk.Button(self, bootstyle='primary-outline', text='Add Custom Nation', command=lambda: InputToplevel(self, 'Add Custom Nation', UI_CONFIG_CUSTOMNATION, 1, target_location=self.custom_nation_list, parent_widget=self))
        add_custom.pack(fill='both', expand=False, side='left')
        add_generic = ttk.Button(self, bootstyle='primary-outline', text='Add Generic Start', command=lambda: InputToplevel(self, 'Add Generic Start', UI_CONFIG_GENERICNATION, 1, target_location=self.generic_nation_list, parent_widget=self))
        add_generic.pack(fill='both', expand=False, side='left')

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

                internal_variable = ttk.IntVar()
                internal_variable.set(j)

                new_frame = ttk.Frame(self)
                self.wrap_frame.window_create(window=new_frame, index='end')
                self.miniframes.append(new_frame)
                # self.miniframes[-1].pack(fill='both', expand=False, side='left')

                if i == 0:
                    text = nation[1]
                else:
                    text = f'Generic Nation {j+1}'

                self.nation_inputs[i] = ttk.Button(self.miniframes[-1], text=text, bootstyle=f'{bootstyle[i]}')
                self.nation_inputs[i].pack(fill='both', expand=False, side='left')

                if self.disciples:
                    xj = ttk.Combobox(self.miniframes[-1], values=TEAMS, textvariable=ttk.StringVar(), justify=ttk.CENTER, bootstyle=f'outline-toolbutton-{bootstyle[i]}', width=2)
                    xj.pack(fill='both', expand=False, side='left')
                    xj.set(TEAMS[0])

                if i == 0:
                    xx = ttk.Checkbutton(self.miniframes[-1], text='X', bootstyle=f'outline-toolbutton-{bootstyle[i]}', command=lambda iv=internal_variable: self.remove(self.custom_nation_list, iv))
                else:
                    xx = ttk.Checkbutton(self.miniframes[-1], text='X', bootstyle=f'outline-toolbutton-{bootstyle[i]}', command=lambda iv=internal_variable: self.remove(self.generic_nation_list, iv))
                xx.pack(fill='both', expand=False, side='left')

    def remove(self, nation_list, j):
        nation_list.pop(j.get())
        self.update()


class EntryScaleWidget(ttk.Frame):

    def __init__(self, master, variable, from_, to, state):
        self.master = master
        self.variable = variable
        super().__init__(master=master)
        self.entry = ttk.Entry(self, state=state, width=3, textvariable=self.variable, justify=ttk.CENTER)
        self.scale = ttk.Scale(self, orient=ttk.HORIZONTAL, variable=variable, from_=from_, to=to, length=120, state=state, command=self.slider_callback)
        self.entry.pack(fill='both', expand=False, side='left')
        self.scale.pack(fill='both', expand=False, side='left')

    def slider_callback(self, event):
        self.variable.set(str(int(float(self.variable.get()))))

    def set(self, i):
        self.variable.set(i)

    def get(self):
        return int(self.variable.get())


class TerrainWidget(ttk.Frame):

    def __init__(self, master):
        super().__init__(master=master)

        self.terrain_int = ttk.IntVar()
        ttk.Label(self, text='Terrain Integer', anchor="e").pack(fill='both', expand=False, side='left')
        ttk.Entry(self, textvariable=self.terrain_int, state=ttk.READONLY).pack(fill='both', expand=False, side='left')

        self.options = dict()
        self.variables = dict()
        for i, (power, terrain_int, text) in enumerate(TERRAIN_PRIMARY):
            self.variables[i] = ttk.IntVar()
            self.options[i] = ttk.Checkbutton(self, text=text, bootstyle="primary-outline-toolbutton", variable=self.variables[i], command=self.update)
            self.options[i].pack(fill='both', expand=False, side='left')

    def update(self):
        terrain_int = 0
        for i, button in enumerate(self.options):
            if self.variables[i].get():
                terrain_int += TERRAIN_PRIMARY[i][1]
        self.terrain_int.set(terrain_int)


class IllwinterDropdownWidget(ttk.Frame):

    def __init__(self, master, data_type):
        super().__init__(master=master)

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

        ttk.Label(self, text=text, anchor="e").pack(fill='both', expand=False, side='left')

        self.variable = ttk.StringVar()
        self.input = ttk.Combobox(self, values=entries, textvariable=self.variable, state=ttk.READONLY)
        self.input.pack(fill='both', expand=False, side='left')
        self.input.set(entries[0])

    def get(self):
        return self.get_dict[self.variable]


class GeneratorInfoWidget(ttk.Frame):

    def __init__(self, master):
        super().__init__(master=master)

        self.labels = dict()
        self.variables = dict()
        self.metrics = dict()

        ttk.Button(self, text='Refresh', command=self.refresh).pack(fill=X, expand=False, side=TOP)

        GENERATOR_INFO = [['Number of provinces', 'text'],
                          ['Number of water provinces', 'text'],
                          ['Number of cave provinces', 'text'],
                          ['Provinces per player', 'text'],
                          ['Gold per player', 'text']]

        for i, (text, tooltip) in enumerate(GENERATOR_INFO):

            self.labels[i] = ttk.Label(self, text=text)
            self.labels[i].pack(fill=X, expand=False, side=TOP)

            self.variables[i] = ttk.StringVar()
            self.metrics[i] = ttk.Entry(self,  width=6, textvariable=self.variables[i], justify=ttk.CENTER)
            self.metrics[i].pack(fill=X, expand=False, side=TOP)

            ToolTip(self.labels[i], text=tooltip, delay=TOOLTIP_DELAY)

        self.labels[i+1] = ttk.Label(self, text='Input Issues?')
        self.labels[i+1].pack(fill=X, expand=False, side=TOP)

        self.metrics[i+1] = ttk.Entry(self, justify=ttk.CENTER)
        self.metrics[i+1].pack(fill=X, expand=False, side=TOP)

    def refresh(self):

        settings_dict = self.master.master.master.inputs
        num_players = len(settings_dict['vanilla_nations'].get()) + len(settings_dict['custom_nations'].custom_nation_list) + len(settings_dict['custom_nations'].generic_nation_list)
        if num_players == 0:
            num_players = 1
        water_provs = settings_dict['water_region_num'].get() * REGION_WATER_INFO[WATER_REGIONS.index(settings_dict['water_region_type'].get())][2] + 0.05 * num_players * settings_dict['periphery_size'].get() * settings_dict['player_neighbours'].get()
        cave_provs = settings_dict['cave_region_num'].get() * REGION_CAVE_INFO[CAVE_REGIONS.index(settings_dict['cave_region_type'].get())][2]
        num_provs = num_players * settings_dict['homeland_size'].get() + 0.5 * num_players * settings_dict['periphery_size'].get() * settings_dict['player_neighbours'].get() + settings_dict['throne_region_num'].get() + settings_dict['water_region_num'].get() * REGION_WATER_INFO[WATER_REGIONS.index(settings_dict['water_region_type'].get())][2] + cave_provs
        provs_per_player = num_provs / num_players
        gold_per_player = 300 + AGE_POPULATION_MODIFIERS[AGES.index(settings_dict['vanilla_nations'].age.get())] * 100 * num_provs / num_players

        def error_check():
            message = ''
            error = False
            if settings_dict['homeland_size'].get() <= settings_dict['cap_connections'].get():
                message += 'Error: Homeland size must be greater than cap connections  '
                error = True
            if [num_players, settings_dict['player_neighbours'].get()] in NOT_AVAILABLE_GRAPHS:
                message += 'Error: Invalid combination of players and neighbours  '
                error = True
            if error:
                return message
            else:
                return 'You\'re good'

        for i, j in enumerate(self.metrics):
            entry = self.metrics[j]

            if i == 0:
                entry.delete(0, END)
                entry.insert(1, str(num_provs))
            elif i == 1:
                entry.delete(0, END)
                entry.insert(1, str(water_provs))
            elif i == 2:
                entry.delete(0, END)
                entry.insert(1, str(cave_provs))
            elif i == 3:
                entry.delete(0, END)
                entry.insert(1, str(provs_per_player))
            elif i == 4:
                entry.delete(0, END)
                entry.insert(1, str(gold_per_player))
            elif i == 5:
                message = error_check()
                entry.delete(0, END)
                entry.insert(1, str(message))
