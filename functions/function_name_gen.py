from DreamAtlas import *


def DreamAtlas_name_gen(province_lists):

    for province_list in province_lists:
        for province in province_list:

            name = ''

            province.has_commands = True
            province.name = name