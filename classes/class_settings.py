
class DreamAtlasSettings:

    def __init__(self, index: int):  # DreamAtlas generator settings

        self.index = index
        self.seed: int = 0
        self.description: str = None
        self.map_title: str = None
        self.ygg_description: str = None
        self.ygg_icon: str = None

        self.homeland_size: int = None
        self.cap_connections: int = None
        self.player_neighbours: int = None
        self.periphery_size: int = None
        self.throne_region_num: int = None
        self.water_region_type: int = None
        self.water_region_num: int = None
        self.cave_region_type: int = None
        self.cave_region_num: int = None
        self.vast_region_num: int = None

        self.art_style: int = None
        self.wraparound: int = None
        self.pop_balancing: int = None
        self.site_frequency: int = None
        self.vanilla_nations: list = list()
        self.custom_nations: list = list()
        self.generic_nations: list = list()
        self.age: int = 0
        self.disciples: bool = False
        self.omniscience: bool = False

    def load_file(self, filename):

        self.__init__(self.index)  # Reset class

        with open(filename, 'r') as f:
            for _ in f.readlines():
                if _[0] == '#':  # Only do anything if the line starts with a command tag
                    _ = _.split()
                    attribute = _[0].strip('#')
                    if attribute == 'vanilla_nation':
                        self.vanilla_nations.append([int(_[1]), int(_[2])])
                    elif attribute == 'custom_nation':
                        self.custom_nations.append([int(_[1]), str(_[2]), str(_[3]), int(_[4]), int(_[5]), int(_[6]), int(_[7]), int(_[8])])
                    elif attribute == 'generic_nation':
                        self.generic_nations.append([int(_[1]), int(_[2]), int(_[3]), int(_[4]), int(_[5])])
                    else:
                        try:
                            setattr(self, attribute, int(_[1]))
                            continue
                        except ValueError:
                            pass
                        try:
                            setattr(self, attribute, _[1])
                            continue
                        except ValueError:
                            pass
                        raise Exception(f'Input error in settings file: {attribute}')

    def save_file(self, filename):

        with open(filename, 'w') as f:  # Writes all the settings to a file
            for attribute in self.__dict__:
                if attribute == 'nations':
                    for i in getattr(self, attribute):
                        f.write(f'#nation {i[0]} {i[1]}\n')
                elif attribute == 'custom_nations':
                    for i in getattr(self, attribute):
                        f.write(f'#customnation {i[0]} {i[1]}\n')
                else:
                    f.write(f'#{attribute} %{getattr(self, attribute)}\n')

    def __str__(self):

        string = f'\nType - {type(self)}\n\n'
        for key in self.__dict__:
            string += f'{key} : {self.__dict__[key]}\n'

        return string
