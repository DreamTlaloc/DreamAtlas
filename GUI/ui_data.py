import ttkbootstrap as ttk

# Info to build UI dynamically [attribute, type, widget, label, options, active]
UI_CONFIG_CONNECTION = {
    'label_frames': [['Connection', ['connected_provinces', 'connection_int']]],
    'buttons': [0, 5],
    'attributes': {
        'connected_provinces': [tuple[int, int], 0, 'Connected Provinces', None, 1, 'Enter the IDs of connected provinces'],
        'connection_int': [int, 6, 'Connection Type', None, 1, 'Select the type of connection between provinces']
    }
}

UI_CONFIG_CUSTOMNATION = {
    'label_frames': [
        ['Nation Info', ['index', 'name', 'tagline']],
        ['Capital Terrain', ['terrain']],
        ['Homeland Info', ['terrain_profile', 'layout', 'home_plane']]],
    'buttons': [1, 5, 6],
    'attributes': {
        'index': [int, 0, 'Nation Number', None, 1, 'Enter the unique number for the nation'],
        'name': [str, 0, 'Name', None, 1, 'Enter the name of the nation'],
        'tagline': [str, 0, 'Tagline', None, 1, 'Enter a short description or slogan for the nation'],

        'terrain': [int, 7, 'Capital Terrain', None, 1, 'Select the terrain type for the nation\'s capital'],

        'terrain_profile': [int, 1, 'Terrain Preference', ['Balanced', 'Plains', 'Forest', 'Mountains', 'Desert', 'Swamp', 'Karst'], 1, 'Select the preferred terrain type for the nation'],
        'layout': [int, 1, 'Layout', ['Land', 'Cave', 'Coast', 'Island', 'Deeps', 'Shallows', 'Lakes'], 1, 'Select the layout type for the nation\'s homeland'],
        'home_plane': [int, 1, 'Home Plane', ['Surface', 'Underground'], 1, 'Select the plane where the nation resides']
    }
}

UI_CONFIG_GENERICNATION = {
    'label_frames': [
        ['Capital Terrain', ['terrain']],
        ['Info', ['terrain_profile', 'layout', 'home_plane']]],
    'buttons': [1, 5, 6],
    'attributes': {

        'terrain': [int, 7, 'Capital Terrain', None, 1, 'Select the terrain type for the nation\'s capital'],

        'terrain_profile': [int, 1, 'Terrain Preference', ['Balanced', 'Plains', 'Forest', 'Mountains', 'Desert', 'Swamp', 'Karst'], 1, 'Select the preferred terrain type for the nation'],
        'layout': [int, 1, 'Layout', ['Land', 'Cave', 'Coast', 'Island', 'Deeps', 'Shallows', 'Lakes'], 1, 'Select the layout type for the nation\'s homeland'],
        'home_plane': [int, 1, 'Home Plane', ['Surface', 'Underground'], 1, 'Select the plane where the nation resides']
    }
}

UI_CONFIG_PROVINCE = {
    'label_frames': [
        ['Province info', ['index', 'name', 'plane', 'parent_region', 'unrest', 'population', 'defence']],
        ['Terrain', ['terrain_int']],
        ['Province info', ['poptype', 'fort']],
        ['Province attributes', ['capital_location', 'killfeatures', 'temple', 'lab']]],
    'buttons': [0, 5],
    'attributes': {
        'index': [int, 0, 'Province Number', None, 1, 'Enter the unique number for the province'],
        'name': [str, 0, 'Province Name', None, 1, 'Enter the name of the province'],
        'plane': [int, 0, 'Plane', None, 0, 'Enter the plane ID where the province is located'],
        'parent_region': [int, 0, 'Parent Region', None, 0, 'Enter the ID of the parent region'],
        'unrest': [int, 0, 'Unrest', None, 0, 'Enter the level of unrest in the province'],
        'population': [int, 0, 'Population', None, 1, 'Enter the population of the province'],
        'defence': [int, 0, 'Defence', None, 0, 'Enter the defence level of the province'],

        'terrain_int': [int, 7, 'Terrain', None, 1, 'Select the terrain type for the province'],

        'capital_location': [int, 3, 'Capital Location Start', None, 0, 'Enter the starting location for the capital'],
        'killfeatures': [int, 3, 'No features', None, 0, 'Select if the province has no features'],
        'temple': [int, 3, 'Temple', None, 0, 'Select if the province has a temple'],
        'lab': [int, 3, 'Lab', None, 0, 'Select if the province has a lab'],

        'poptype'       : [int, 6, 'Poptype', ['Pops go here'], 0, 'Select the population type for the province'],
        # 'owner'         : [int, 6, 'Owner', ['Owners go here'], 0, 'Select the owner of the province'],
        # 'capital_nation': [int, 6, 'Nation Start', ['Natstart go here'], 0, 'Select the starting nation for the province'],
        'fort'          : [int, 6, 'Fort', ['Fort go here'], 0, 'Select the fort type for the province']
    }
}

UI_CONFIG_REGION = [
    ['index', int, 0, 'Region Number', None, 0, 'Enter the unique number for the region'],
    ['name', str, 0, 'Province Name', None, 1, 'Enter the name of the region'],
    ['plane', int, 0, 'Plane', None, 0, 'Enter the plane ID where the region is located'],
    ['coordinates', list, 0, 'Coordinates', None, 0, 'Enter the coordinates of the region'],
    ['terrain_int', int, 0, 'Terrain Integer', None, 0, 'Select the terrain type for the region']
]

UI_CONFIG_SETTINGS = {
    'label_frames': [
        ['Map Info', ['map_title', 'seed']],
        ['General Settings', ['art_style', 'wraparound', 'pop_balancing', 'site_frequency', 'cap_connections', 'player_neighbours']],
        ['Region Settings', ['homeland_size', 'periphery_size', 'throne_region_num', 'water_region_num', 'cave_region_num', 'vast_region_num', 'water_region_type', 'cave_region_type']],
        ['Additional Options', ['disciples', 'omniscience']],
        ['Nations & Teams', ['vanilla_nations']],
        ['Generic/Custom Nations', ['custom_nations']],
        ['Estimates', ['generation_info']]],
    'buttons': [2, 3, 4, 5, 6],
    'attributes': {
        'map_title': [str, 0, 'Map Title', None, 1, 'Enter the title of the map'],
        'seed': [int, 0, 'Seed', None, 1, 'Enter the random seed for map generation'],
        # 'description': [str, 0, 'Description', None, 1, 'Enter a description for the map'],

        'art_style': [int, 1, 'Art Style', ['.d6m'], 1, 'Select the art style for the map'],
        'wraparound': [int, 1, 'Wraparound', ['None', 'Horizontal', 'Vertical', 'Full'], 1, 'Select the wraparound type for the map'],
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

        'disciples': [int, 3, 'Disciples', None, 0, 'Toggle disciples mode'],
        'omniscience': [int, 3, 'Omniscience', None, 1, 'Toggle creating a hidden omniscience start'],

        'vanilla_nations': [list, 4, 'Nations & Teams', None, 1, 'Select the vanilla nations and teams\nOnly nations from the selected age will be used'],
        'custom_nations': [list, 5, 'Custom/Generic Nations', None, 1, 'Select the custom or generic nations']
    }
}

TEAMS = ['-', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20']
TERRAIN_PRIMARY = [
    [None, 0, 'Plains'], [2, 4, 'Sea'], [4, 16, 'Highlands/Gorge'], [5, 32, 'Swamp'], [6, 64, 'Waste'],
    [7, 128, 'Forest/Kelp'], [8, 256, 'Farm'], [11, 2048, 'Deep sea'], [12, 4096, 'Cave'], [23, 8388608, 'Mountains'],
    [30, 1073741824, 'Warmer'], [31, 2147483648, 'Colder'], [33, 8589934592, 'Vast'],
    [34, 17179869184, 'Infernal waste'], [35, 34359738368, 'Void'], [38, 274877906944, 'Flooded']
]
CAVE_REGIONS = ['None', 'Grottos', 'Tunnels', 'Caverns']
WATER_REGIONS = ['None', 'Lakes', 'Seas', 'Oceans']
EXPLORER_REGIONS = ["Homelands", "Peripheries", "Thrones", "Water", "Caves", "Vasts", "Blockers"]

TOOLTIP_DELAY = 500

UI_STATES = (ttk.DISABLED, ttk.NORMAL, ttk.HIDDEN)
UI_CONNECTION_COLOURS = {0: 'black', 33: 'red', 2: 'blue', 4: 'grey', 8: 'green', 16: 'brown', 36: 'red', 3: 'pink'}  # [0, 'Standard border'], [33, 'Mountain pass'], [2, 'River border'], [4, 'Impassable'], [8, 'Road'], [16, 'River bridge'], [36, 'Impassable mountain'], [3, 'Waterfalls']