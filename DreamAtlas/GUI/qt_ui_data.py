THEME_FANTASY = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', sans-serif;
    font-size: 10pt;
}
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 4px;
    margin-top: 8px;
    font-weight: bold;
    color: #89b4fa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}
QTreeWidget {
    background-color: #181825;
    border: none;
    color: #cdd6f4;
}
QTreeWidget::item:selected {
    background-color: #313244;
}
QScrollArea {
    background-color: #181825;
    border: none;
    color: #181825;
}
QScrollBar:vertical {
    background: #181825;
    width: 10px;
}
QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 5px;
}
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 8px;
}
QPushButton:hover    { background-color: #45475a; }
QPushButton:checked  { background-color: #89b4fa; color: #1e1e2e; border-color: #89b4fa; }
QPushButton:disabled { color: #585b70; border-color: #313244; }
QCheckBox { spacing: 6px; }
QCheckBox::indicator {
    width: 14px; height: 14px;
    border: 1px solid #45475a;
    border-radius: 3px;
    background: #181825;
}
QCheckBox::indicator:checked { background: #89b4fa; }
QCheckBox:disabled { color: #585b70; }
QComboBox {
    border: 1px solid #45475a;
}
QLineEdit {
    border: 1px solid #45475a;
}
QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
}
QMenuBar::item:selected { background-color: #313244; }
QMenu {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #45475a;
}
QMenu::item:selected { background-color: #313244; }
QSplitter::handle { background: #45475a; }
"""


UI_CONFIG_PROVINCE = {
    'label_frames': [
        ['Province info', ['index', 'name', 'unrest', 'population']],
        ['Terrain', ['terrain_int']],
        ['Province info', ['poptype', 'fort']],
        ['Province attributes', ['killfeatures', 'temple', 'lab']]],
    'buttons': [0, 5],
    'attributes': {
        'index': [int, 0, 'Province Number', None, 0, 'Enter the unique number for the province'],
        'name': [str, 0, 'Province Name', None, 1, 'Enter the name of the province'],
        # 'plane': [int, 0, 'Plane', None, 1, 'Enter the plane ID where the province is located'],
        # 'parent_region': [int, 0, 'Parent Region', None, 1, 'Enter the ID of the parent region'],
        'unrest': [int, 0, 'Unrest', None, 1, 'Enter the level of unrest in the province'],
        'population': [int, 0, 'Population', None, 1, 'Enter the population of the province'],

        'terrain_int': [int, 7, 'Terrain', None, 1, 'Select the terrain type for the province'],

        # 'capital_location': [int, 3, 'Good start', None, 1, 'Enter the starting location for the capital'],
        'killfeatures'    : [int, 3, 'No features', None, 1, 'Select if the province has no features'],
        'temple'          : [int, 3, 'Temple', None, 1, 'Select if the province has a temple'],
        'lab'             : [int, 3, 'Lab', None, 1, 'Select if the province has a lab'],

        'poptype'       : [int, 6, 'Poptype', ['Pops go here'], 1, 'Select the population type for the province'],
        # 'owner'         : [int, 6, 'Owner', ['Owners go here'], 1, 'Select the owner of the province'],
        # 'capital_nation': [int, 6, 'Nation Start', ['Natstart go here'], 1, 'Select the starting nation for the province'],
        'fort'          : [int, 6, 'Fort', ['Fort go here'], 1, 'Select the fort type for the province']
    }
}

UI_CONFIG_CONNECTION = {
    'label_frames': [['Connection', ['connected_provinces', 'connection_int']]],
    'buttons': [0, 5],
    'attributes': {
        'connected_provinces': [tuple[int, int], 0, 'Connected Provinces', None, 0, 'Enter the IDs of connected provinces'],
        'connection_int': [int, 6, 'Connection Type', None, 1, 'Select the type of connection between provinces']
    }
}

UI_CONFIG_SETTINGS = {
    'label_frames': [
        ['Map Info', ['map_title', 'seed']],
        ['General Settings', ['art_style', 'pop_balancing', 'site_frequency', 'cap_connections', 'player_neighbours']],
        ['Region Settings', ['homeland_size', 'periphery_size', 'throne_region_num', 'water_region_num', 'cave_region_num', 'vast_region_num', 'water_region_type', 'cave_region_type']],
        ['Additional Options', ['disciples', 'omniscience']],
        ['Nations & Teams', ['vanilla_nations']],
        ['Generic/Custom Nations', ['custom_nations']],
        ['Estimates', ['generation_info']]],
    'buttons': [2, 3, 4, 6],
    'attributes': {
        'map_title': [str, 0, 'Map Title', None, 1, 'Enter the title of the map'],
        'seed': [int, 0, 'Seed', None, 1, 'Enter the random seed for map generation'],

        'art_style': [int, 1, 'Art Style', ['.d6m'], 1, 'Select the art style for the map'],
        'pop_balancing': [int, 1, 'Balance', ['Vanilla', 'DreamAtlas'], 1, 'Select the balancing method\nVanilla - No balancing\nDreamAtlas (recommended) - Fair population and terrain balance'],
        'cave_region_type': [int, 1, 'Cave Type', ['None', 'Grottos', 'Tunnels', 'Caverns'], 1, 'Select the type of cave regions\nNone - No cave regions\nGrottos - 1 province per region\nTunnels - 3 provinces per region\nCaverns - 6 provinces per region'],
        'water_region_type': [int, 1, 'Water Type', ['None', 'Lakes', 'Seas', 'Oceans'], 1, 'Select the type of water regions\nNone - No water regions\nLakes - 1 province per region\nSeas - 3 provinces per region\nOceans - 5 provinces per region'],

        'site_frequency': [int, 2, 'Site Frequency', [40, 100], 1, 'Select the frequency of magic sites on the map'],
        'cap_connections': [int, 2, 'Capital Connections', [4, 8], 1, 'Select the number of provinces in each cap circle (must be less than the size of the homeland)'],
        'player_neighbours': [int, 2, 'Player Neighbours', [3, 6], 1, 'Select the number of neighbours for each player'],
        'homeland_size': [int, 2, 'Homeland Size', [6, 12], 1, 'Select the size of the homeland regions\nThese are the regions around each players capital'],
        'periphery_size': [int, 2, 'Periphery Size', [1, 8], 1, 'Select the size of the periphery regions\nThese are the regions connecting different players'],
        'throne_region_num': [int, 2, 'Thrones', [1, 32], 1, 'Select the number of thrones'],
        'water_region_num': [int, 2, 'Water Regions', [0, 30], 1, 'Select the number of water regions'],
        'cave_region_num': [int, 2, 'Cave Regions', [0, 30], 1, 'Select the number of cave regions'],
        'vast_region_num': [int, 2, 'Vast Regions', [0, 30], 1, 'Select the number of vast regions\nThese regions are empty and uncontrollable but can be traversed'],

        'disciples': [int, 3, 'Disciples', None, 1, 'Toggle disciples mode'],
        'omniscience': [int, 3, 'Omniscience', None, 1, 'Toggle creating a hidden omniscience start'],

        'vanilla_nations': [list, 4, 'Nations & Teams', None, 1, 'Select the vanilla nations and teams\nOnly nations from the selected age will be used'],
        'custom_nations': [list, 5, 'Custom/Generic Nations', None, 1, 'Select the custom or generic nations']
    }
}


INTERFACE_TITLE = "DreamAtlas v2.0.0"
INTERFACE_ICON = 'DreamAtlas/databases/ui_images/DreamAtlasLogoSquare.png'

EXPLORER_REGIONS = ["Homelands", "Peripheries", "Thrones", "Water", "Caves", "Vasts", "Blockers"]

CONNECTION_COLOURS = {0: 'yellow', 33: 'red', 2: 'blue', 4: '#808080', 8: 'green', 16: 'cyan', 36: '#808080'}

DISPLAY_OPTIONS = ['Show Nodes', 'Show Connections', 'Show Borders', 'Show Capitals', 'Show Thrones', 'Terrain Icons']
DISPLAY_TAGS = ['nodes', 'connections', 'borders', 'capitals', 'thrones', 'info']
DISPLAY_STATES = [1, 1, 1, 1, 1, 1]

LENSE_KEY = {'z': 0, 'x': 1, 'c': 2, 'v': 3, 'b': 4, 'n': 5}