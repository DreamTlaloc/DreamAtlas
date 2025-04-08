from . import *


class Nation:

    def __init__(self, nation_data):

        # The nation index is used to lookup all the other properties of a nation from the .__init__ constants
        self.index, self.team = nation_data
        self.iid = None

        # Nation info
        for entry in ALL_NATIONS:
            if entry[0] == self.index:
                self.name = entry[1]
                self.tagline = entry[2]

        # Nation homeland config
        for entry in HOMELANDS_INFO:
            if entry[0] == self.index:
                self.terrain_profile = entry[1]
                self.layout = entry[2]
                self.terrain = entry[3]
                self.home_plane = entry[4]

    def __str__(self):  # Printing the class returns this

        string = f'\nType - {type(self)}\n\n'
        for key in self.__dict__:
            string += f'{key} : {self.__dict__[key]}\n'

        return string


class CustomNation:

    def __init__(self, custom_nation_data):
        self.index, self.name, self.tagline, self.terrain, terrain_index, layout_index, self.home_plane, self.team = custom_nation_data
        self.terrain_profile = TERRAIN_PREFERENCES[terrain_index]
        self.layout = LAYOUT_PREFERENCES[layout_index]
        self.iid = None

    def __str__(self):  # Printing the class returns this

        string = f'\nType - {type(self)}\n\n'
        for key in self.__dict__:
            string += f'{key} : {self.__dict__[key]}\n'

        return string


class GenericNation:

    def __init__(self, generic_nation_data):
        self.terrain, terrain_index, layout_index, self.home_plane, self.team = generic_nation_data
        self.terrain_profile = TERRAIN_PREFERENCES[terrain_index]
        self.layout = LAYOUT_PREFERENCES[layout_index]
        self.name = 'Generic Nation'
        self.iid = None

    def __str__(self):  # Printing the class returns this

        string = f'\nType - {type(self)}\n\n'
        for key in self.__dict__:
            string += f'{key} : {self.__dict__[key]}\n'

        return string
