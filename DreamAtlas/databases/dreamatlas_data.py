import numpy as np
import pathlib
import os
import sys
import matplotlib as mpl

# Terrain preference vector is the weighting for each type of terrain
TERRAIN_PREF_BITS = [0, 16, 32, 64, 128, 256]
TERRAIN_PREFERENCES = [         # TERRAIN_PREF_XXXX = [plains, highlands, swamp, waste, forest, farm]
    [5, 1, 1, 1, 4, 2],         # Balanced
    [10, 1, 2, 1, 2, 2],        # Plains
    [3, 1, 1, 0.5, 6, 2],       # Forest
    [3, 4, 1, 1, 5, 2],         # Mountains
    [3, 1, 1, 2, 1, 2],         # Desert
    [3, 1, 3, 0.5, 4, 2],       # Swamp
]
TERRAIN_PREF_BALANCED, TERRAIN_PREF_PLAINS, TERRAIN_PREF_FOREST, TERRAIN_PREF_MOUNTAINS, TERRAIN_PREF_DESERT, TERRAIN_PREF_SWAMP = TERRAIN_PREFERENCES

# Layout preference vector informs the land-sea split
LAYOUT_PREFERENCES = [  # LAYOUT_PREF_XXXX = [cap terrain, cap provinces ratio, extra provinces ratio]
    [1, 1.0, 0.85],         # Land
    [1, 1.0, 1.0],          # Cave
    [1, 0.9, 0.8],          # Coast
    [1, 0.0, 0.9],          # Island
    [0, 0.0, 0.0],          # Deeps
    [0, 0.1, 0.6],          # Shallows
    [1, 0.9, 0.5]           # Lakes
]
LAYOUT_PREF_LAND, LAYOUT_PREF_CAVE, LAYOUT_PREF_COAST, LAYOUT_PREF_ISLAND, LAYOUT_PREF_DEEPS, LAYOUT_PREF_SHALLOWS, LAYOUT_PREF_LAKES = LAYOUT_PREFERENCES

REGION_TYPE = ['Throne', 'Homeland', 'Periphery', 'Water', 'Cave', 'Vast', 'Blocker']
REGION_WATER_INFO = [
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_DEEPS, 0, 1],
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_DEEPS, 1, 1],
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_DEEPS, 3, 2],
    [TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_DEEPS, 5, 3]
]

REGION_CAVE_INFO = [
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1, 0],
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 1, 1, 1],
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 3, 1, 2],
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 6, 4, 3]
]

REGION_VAST_INFO = [17179869184, 17179869184, 17179869184, 17179869184, 17179869184, 17179869184]

# Blocker vector informs how different blockers are created
REGION_BLOCKER_INFO = {  # BLOCKER_XXXX = [plane, terrain int, region_size, anchor_connections]
    6: [1, 16 + 8388608 + 68719476736 + 549755813888, 3, 2],    # Mountain Range
    8: [2, 4096 + 68719476736 + 576460752303423488, 4, 3]       # Cave Wall
}

HOMELANDS_INFO = [  # Homelands format: [Nation index, terrain preference, layout preference, capital terrain int, plane]
    # EA NATIONS
    [5, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],             # Arcoscephale
    [6, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],             # Mekone
    [7, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],             # Pangaea
    [8, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],             # Ermor
    [9, TERRAIN_PREF_PLAINS, LAYOUT_PREF_LAND, 0, 1],               # Sauromatia
    [10, TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST, 0, 1],           # Fomoria
    [11, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 128, 1],          # Tir na nog
    [12, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 128, 1],          # Marverni
    [13, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 128, 1],         # Ulm
    [14, TERRAIN_PREF_FOREST, LAYOUT_PREF_CAVE, 4224, 2],           # Pyrene
    [15, TERRAIN_PREF_SWAMP, LAYOUT_PREF_CAVE, 4096, 2],            # Agartha
    [16, TERRAIN_PREF_DESERT, LAYOUT_PREF_CAVE, 8392704, 2],        # Abysia
    [17, TERRAIN_PREF_DESERT, LAYOUT_PREF_LAND, 64, 1],             # Hinnom
    [18, TERRAIN_PREF_DESERT, LAYOUT_PREF_LAND, 64, 1],             # Ubar
    [19, TERRAIN_PREF_SWAMP, LAYOUT_PREF_LAND, 0, 1],               # Ur
    [20, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 8388608, 1],        # Kailasa
    [21, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],            # Lanka
    [22, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Tien Chi
    [23, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 8388608, 1],     # Yomi
    [24, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 8388608, 1],     # Caelum
    [25, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],            # Mictlan
    [26, TERRAIN_PREF_BALANCED, LAYOUT_PREF_CAVE, 4224, 2],         # Xibalba
    [27, TERRAIN_PREF_SWAMP, LAYOUT_PREF_LAND, 32, 1],              # Ctis
    [28, TERRAIN_PREF_PLAINS, LAYOUT_PREF_LAND, 0, 1],              # Machaka
    [29, TERRAIN_PREF_DESERT, LAYOUT_PREF_COAST, 0, 1],             # Berytos
    [30, TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST, 0, 1],           # Vanheim
    [31, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Helheim
    [32, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 0, 1],              # Rus
    [33, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Niefelheim
    [34, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Muspelheim
    [40, TERRAIN_PREF_FOREST, LAYOUT_PREF_SHALLOWS, 4, 1],          # Pelagia
    [41, TERRAIN_PREF_FOREST, LAYOUT_PREF_SHALLOWS, 132, 1],        # Oceania
    [42, TERRAIN_PREF_BALANCED, LAYOUT_PREF_SHALLOWS, 4, 1],        # Therodos
    [43, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_DEEPS, 2052, 1],       # Atlantis
    [44, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_DEEPS, 2052, 1],       # Ryleh

    # MA NATIONS
    [50, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Arcoscephale
    [51, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Phlegra
    [52, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],            # Pangaea
    [53, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],            # Asphodel
    [54, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Ermor
    [55, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Sceleria
    [56, TERRAIN_PREF_SWAMP, LAYOUT_PREF_LAND, 0, 1],               # Pythium
    [57, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],            # Man
    [58, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],            # Eriu
    [59, TERRAIN_PREF_BALANCED, LAYOUT_PREF_CAVE, 4096, 2],         # Agartha
    [60, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 0, 1],           # Ulm
    [61, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Marignon
    [62, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 128, 1],         # Pyrene
    [63, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 8392704, 2],      # Abysia
    [64, TERRAIN_PREF_DESERT, LAYOUT_PREF_LAND, 64, 1],             # Ashdod
    [65, TERRAIN_PREF_DESERT, LAYOUT_PREF_LAND, 64, 1],             # Naba
    [66, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Uruk
    [67, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Ind
    [68, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],            # Bandar Log
    [69, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Tien Chi
    [70, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 8388608, 1],     # Shinuyama
    [71, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 8388608, 1],     # Caelum
    [72, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 8388608, 1],     # Nazca
    [73, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Mictlan
    [74, TERRAIN_PREF_SWAMP, LAYOUT_PREF_CAVE, 4128, 2],            # Xibalba
    [75, TERRAIN_PREF_SWAMP, LAYOUT_PREF_LAND, 32, 1],              # Ctis
    [76, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 0, 1],              # Machaka
    [77, TERRAIN_PREF_BALANCED, LAYOUT_PREF_ISLAND, 0, 1],          # Phaeacia
    [78, TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST, 0, 1],           # Vanheim
    [79, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 0, 1],              # Vanarus
    [80, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 0, 1],              # Jotunheim
    [81, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Nidavangr
    [85, TERRAIN_PREF_BALANCED, LAYOUT_PREF_SHALLOWS, 4, 1],        # Ys
    [86, TERRAIN_PREF_FOREST, LAYOUT_PREF_SHALLOWS, 4, 1],          # Pelagia
    [87, TERRAIN_PREF_FOREST, LAYOUT_PREF_SHALLOWS, 132, 1],        # Oceania
    [88, TERRAIN_PREF_BALANCED, LAYOUT_PREF_DEEPS, 2052, 1],        # Atlantis
    [89, TERRAIN_PREF_BALANCED, LAYOUT_PREF_DEEPS, 2052, 1],        # Ryleh

    # LA NATIONS
    [95, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Arcoscephale
    [96, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 8388608, 1],      # Phlegra
    [97, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],            # Pangaea
    [98, TERRAIN_PREF_SWAMP, LAYOUT_PREF_LAND, 0, 1],               # Pythium
    [99, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],            # Lemuria
    [100, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 0, 1],             # Man
    [101, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 0, 1],          # Ulm
    [102, TERRAIN_PREF_BALANCED, LAYOUT_PREF_CAVE, 4096, 2],        # Agartha
    [103, TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST, 0, 1],          # Marignon
    [104, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 8392704, 2],     # Abysia
    [105, TERRAIN_PREF_PLAINS, LAYOUT_PREF_LAND, 0, 1],             # Ragha
    [106, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 8388608, 1],    # Caelum
    [107, TERRAIN_PREF_DESERT, LAYOUT_PREF_LAND, 64, 1],            # Gath
    [108, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],           # Patala
    [109, TERRAIN_PREF_PLAINS, LAYOUT_PREF_LAND, 0, 1],             # Tien Chi
    [110, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_COAST, 0, 1],         # Jomon
    [111, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],           # Mictlan
    [112, TERRAIN_PREF_BALANCED, LAYOUT_PREF_CAVE, 0, 2],           # Xibalba
    [113, TERRAIN_PREF_DESERT, LAYOUT_PREF_LAND, 32, 1],            # Ctis
    [115, TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST, 0, 1],          # Midgard
    [116, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],           # Bogarus
    [117, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],           # Utgard
    [118, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],           # Vaettiheim
    [119, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],           # Feminie
    [120, TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND, 0, 1],           # Piconye
    [121, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 0, 1],          # Andramania
    [123, TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND, 128, 1],        # Pyrene
    [124, TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND, 128, 1],           # Zemaitia
    [125, TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST, 0, 1],          # Erytheia
    [126, TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST, 0, 1],          # Atlantis
    [127, TERRAIN_PREF_BALANCED, LAYOUT_PREF_DEEPS, 2052, 1]        # Ryleh
]

# Periphery config
PERIPHERY_INFO = [
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_LAND],      # 0 BORDERS
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST],     # 1 COASTLINES
    [TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_LAND],     # 2 MOUNTAINS
    [TERRAIN_PREF_DESERT, LAYOUT_PREF_LAND],        # 3 WASTES
    [TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND],        # 4 DEEPWOODS
    [TERRAIN_PREF_FOREST, LAYOUT_PREF_LAND],        # 5 OVERUNDER
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_ISLAND],    # 6 ARCHIPELAGO
    [TERRAIN_PREF_SWAMP, LAYOUT_PREF_LAKES],        # 7 WETLANDS
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_DEEPS],     # 8 SEABED
    [TERRAIN_PREF_MOUNTAINS, LAYOUT_PREF_DEEPS],    # 9 ABYSS
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_COAST],     # 10 DELTA
    [TERRAIN_PREF_BALANCED, LAYOUT_PREF_DEEPS]      # 11 UNDERSEA
]

TERRAIN_2_HEIGHTS_DICT = {0: 5, 4: -25, 16: 10, 32: 2, 64: 3, 128: 9, 256: 4, 2048: -10, 4096: 20, 8388608: 20, 17179869184: 3, 68719476736: -100}
TERRAIN_2_SHAPES_DICT = {0: 1, 4: 1.1, 8: 0.9, 16: 0.9, 32: 1.1, 64: 1.2, 128: 1.2, 256: 0.9, 2048: 1, 4096: 1.1, 8388608: 1, 17179869184: 1, 68719476736: 1}
TERRAIN_POPULATION_ORDER = {0: 4, 16: 2, 32: 1, 64: 0, 128: 3, 256: 5}  # TERRAIN_PREF_XXXX = [plains, highlands, swamp, waste, forest, farm]

# Connections config [Standard border, Mountain pass, River border, Impassable, Road, River bridge, Impassable mountain]
NEIGHBOUR_SPECIAL_WEIGHTS = [0.7, 0.05, 0.05, 0, 0.05, 0.02, 0.05]

COLOURS_PROVINCES = mpl.colormaps['gist_stern']
COLOURS_REGIONS = mpl.colormaps['tab20']
COLOURS_TERRAIN = mpl.colormaps['terrain']
COLOURS_POPULATION = mpl.colormaps['Greens']
COLOURS_RESOURCES = mpl.colormaps['Oranges']
COLOURS_DICT = {16: 0.75,
                32: 0.22,
                64: 0.55,
                128: 0.3,
                256: 0.4,
                4: 0.1,
                2052: 0.01,
                132: 0.25,
                4096: 0.7,
                4128: 0.2,
                4160: 0.55,
                4224: 0.3,
                8589934592: 0.85,
                68719476736: 0.85}  # Terrain colours

# UNIVERSAL FUNCTIONS AND VARIABLES
########################################################################################################################
if getattr(sys, "frozen", False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable
    ROOT_DIR = pathlib.Path(__file__).parent.parent
    LOAD_DIR = pathlib.Path(sys.executable).parent
    ART_ICON = ROOT_DIR / r'databases/ui_images/DreamAtlasLogoSquare.png'
else:
    # Normal development mode. Use os.getcwd() or __file__ as appropriate in your case...
    ROOT_DIR = pathlib.Path(__file__).parent.parent
    LOAD_DIR = ROOT_DIR
    ART_ICON = ROOT_DIR / r'databases/ui_images/DreamAtlasLogoSquare.png'

AGES = ['Early Age', 'Middle Age', 'Late Age']

CAPITAL_POPULATION = 40000

AGE_POPULATION_MODIFIERS = [0.8, 1.0, 1.2]
AGE_POPULATION_SIZES = [8400, 10500, 12600]  # Hundreds adjustment is to account for vanilla smaller/larger aberration
AVERAGE_POPULATION_SIZES = [5500, 11000, 16500]
RESOURCE_SPECIFIC_TERRAINS = {4224: 1, 4112: 1.6, 4128: 2, 4096: 1, 132: 1, 20: 1.4, 2052: 1.2, 4: 1, 8388608: 2, 128: 1.6, 16: 1.4}

NEIGHBOURS_NO_WRAP = np.array([[0, 0]])
NEIGHBOURS_X_WRAP = np.array([[0, 0], [1, 0], [-1, 0]])
NEIGHBOURS_Y_WRAP = np.array([[0, 0], [0, 1], [0, -1]])
NEIGHBOURS_FULL = np.array([[0, 0], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [0, -1], [-1, -1], [-1, 0]])
NEIGHBOURS = [NEIGHBOURS_NO_WRAP, NEIGHBOURS_X_WRAP, NEIGHBOURS_Y_WRAP, NEIGHBOURS_FULL]

PIXELS_PER_PROVINCE = 53000

DATASET_GRAPHS = [[[] for i in range(7)] for d in range(41)]
AVAILABLE_GRAPHS = np.zeros((41, 7), dtype=np.int8)
vertex, graph_dict = 0, dict()
with open(ROOT_DIR / 'databases/expanded_graphs', 'r') as f:
    for line in f.readlines():
        data = line.split()
        if not data:
            DATASET_GRAPHS[vertex][degree].append(graph_dict)
            AVAILABLE_GRAPHS[vertex, degree] = 1
            vertex = 0
            graph_dict = dict()
            continue
        vertex += 1
        degree = len(data) - 1
        graph_dict[int(data[0].strip(':'))] = [int(x) for x in data[1:]]

NOT_AVAILABLE_GRAPHS = list()
for i, j in np.argwhere(AVAILABLE_GRAPHS == 0):
    NOT_AVAILABLE_GRAPHS.append([i, j])

PERIPHERY_DATA = []
with open(ROOT_DIR / 'databases/peripheries', 'r') as f:
    for line in f.readlines():
        data = line.strip('\n')
        data = data.split('\t')
        PERIPHERY_DATA.append(list(map(int, data)))