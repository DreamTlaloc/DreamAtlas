# DOMINIONS DATA
TERRAIN_DATA = [
    [None, 0, 'Plains'], [0, 1, 'Small province'], [1, 2, 'Large province'], [2, 4, 'Sea'],
    [3, 8, 'Freshwater'], [4, 16, 'Highlands (or gorge)'], [5, 32, 'Swamp'], [6, 64, 'Waste'],
    [7, 128, 'Forest (or kelp forest)'], [8, 256, 'Farm'], [9, 512, 'No start'], [10, 1024, 'Many sites'],
    [11, 2048, 'Deep sea'], [12, 4096, 'Cave'], [13, 8192, 'Fire sites'], [14, 16384, 'Air sites'],
    [15, 32768, 'Water sites'], [16, 65536, 'Earth sites'], [17, 131072, 'Astral sites'],
    [18, 262144, 'Death sites'], [19, 524288, 'Nature sites'], [20, 1048576, 'Glamour sites'],
    [21, 2097152, 'Blood sites'], [22, 4194304, 'Holy Sites'], [23, 8388608, 'Mountains'],
    [25, 33554432, 'Good throne location'], [26, 67108864, 'Good start location'], [27, 134217728, 'Bad throne location'],
    # 28 29
    [30, 1073741824, 'Warmer'], [31, 2147483648, 'Colder'], [32, 4294967296, 'Invisible'], [33, 8589934592, 'Vast'],
    [34, 17179869184, 'Infernal waste'], [35, 34359738368, 'Void'], [36, 68719476736, 'Cave wall'],
    [37, 137438953472, 'Has gate'], [38, 274877906944, 'Flooded'], [39, 549755813888, 'Attackers rout once'],
    # [40, 1099511627776, 'No effect'],
    # [41, 2199023255552, 'No effect'],
    [59, 576460752303423488, 'Cave wall effect/draw as cave'], [60, 1152921504606846976, 'Draw as UW'],
    [61, 2305843009213693952, '???'], [62, 4611686018427387904, '???']

    # 61, 62, 63, 64 worth checking, unlikely to go beyond 64
]

EA_NATIONS = [
    [5, 'Arcoscephale', 'Golden Era'], [6, 'Mekone', 'Brazen Giants'], [7, 'Pangaea', 'Age of Revelry'],
    [8, 'Ermor', 'New Faith'], [9, 'Sauromatia', 'Amazon Queens'], [10, 'Fomoria', 'The Cursed Ones'],
    [11, 'Tir na nog', 'Land of the Ever Young'], [12, 'Marverni', 'Time of Druids'], [13, 'Ulm', 'Enigma of Steel'],
    [14, 'Pyrene', 'Kingdom of the Bekrydes'], [15, 'Agartha', 'Pale Ones'], [16, 'Abysia', 'Children of Flame'],
    [17, 'Hinnom', 'Sons of the Fallen'], [18, 'Ubar', 'Kingdom of the Unseen'], [19, 'Ur', 'The First City'],
    [20, 'Kailasa', 'Rise of the Ape Kings'], [21, 'Lanka', 'Land of Demons'], [22, 'Tien Chi', 'Spring and Autumn'],
    [23, 'Yomi', 'Oni Kings'], [24, 'Caelum', 'Eagle Kings'], [25, 'Mictlan', 'Reign of Blood'],
    [26, 'Xibalba', 'Vigil of the Sun'], [27, 'Ctis', 'Lizard Kings'], [28, 'Machaka', 'Lion Kings'],
    [29, 'Berytos', 'Phoenix Empire'], [30, 'Vanheim', 'Age of Vanir'], [31, 'Helheim', 'Dusk and Death'],
    [32, 'Rus', 'Sons of Heaven'], [33, 'Niefelheim', 'Sons of Winter'], [34, 'Muspelheim', 'Sons of Fire'],
    [40, 'Pelagia', 'Pearl Kings'], [41, 'Oceania', 'Coming of the Capricorns'], [42, 'Therodos', 'Telkhine Spectre'],
    [43, 'Atlantis', 'Emergence of the Deep Ones'], [44, 'Rlyeh', 'Time of Aboleths']
]

MA_NATIONS = [
    [50, 'Arcoscephale', 'The Old Kingdom'], [51, 'Phlegra', 'Deformed Giants'], [52, 'Pangaea', 'Age of Bronze'],
    [53, 'Asphodel', 'Carrion Woods'], [54, 'Ermor', 'Ashen Empire'], [55, 'Sceleria', 'Reformed Empire'],
    [56, 'Pythium', 'Emerald Empire'], [57, 'Man', 'Tower of Avalon'], [58, 'Eriu', 'Last of the Tuatha'],
    [59, 'Agartha', 'Golem Cult'], [60, 'Ulm', 'Forges of Ulm'], [61, 'Marignon', 'Fiery Justice'],
    [62, 'Pyrene', 'Time of the Akelarre'], [63, 'Abysia', 'Blood and Fire'], [64, 'Ashdod', 'Reign of the Anakim'],
    [65, 'Naba', 'Queens of the Desert'], [66, 'Uruk', 'City States'],
    [67, 'Ind', 'Magnificent Kingdom of Exalted Virtue'], [68, 'Bandar Log', 'Land of the Apes'],
    [69, 'Tien Chi', 'Imperial Bureaucracy'], [70, 'Shinuyama', 'Land of the Bakemono'],
    [71, 'Caelum', 'Reign of the Seraphim'], [72, 'Nazca', 'Kingdom of the Sun'],
    [73, 'Mictlan', 'Reign of the Lawgiver'],
    [74, 'Xibalba', 'Flooded Caves'], [75, 'Ctis', 'Miasma'], [76, 'Machaka', 'Reign of Sorcerors'],
    [77, 'Phaeacia', 'Isle of the Dark Ships'], [78, 'Vanheim', 'Arrival of Man'], [79, 'Vanarus', 'Land of the Chuds'],
    [80, 'Jotunheim', 'Iron Woods'], [81, 'Nidavangr', 'Bear, Wolf and Crow'], [85, 'Ys', 'Morgen Queens'],
    [86, 'Pelagia', 'Triton Kings'], [87, 'Oceania', 'Mermidons'], [88, 'Atlantis', 'Kings of the Deep'],
    [89, 'Rlyeh', 'Fallen Star']
]

LA_NATIONS = [
    [95, 'Arcoscephale', 'Sibylline Guidance'], [96, 'Phlegra', 'Sleeping Giants'], [97, 'Pangaea', 'New Era'],
    [98, 'Pythium', 'Serpent Cult'], [99, 'Lemuria', 'Soul Gate'], [100, 'Man', 'Towers of Chelms'],
    [101, 'Ulm', 'Black Forest'], [102, 'Agartha', 'Ktonian Dead'], [103, 'Marignon', 'Conquerors of the Sea'],
    [104, 'Abysia', 'Blood of Humans'], [105, 'Ragha', 'Dual Kingdom'], [106, 'Caelum', 'Return of the Raptors'],
    [107, 'Gath', 'Last of the Giants'], [108, 'Patala', 'Reign of the Nagas'], [109, 'Tien Chi', 'Barbarian Kings'],
    [110, 'Jomon', 'Human Daimyos'], [111, 'Mictlan', 'Blood and Rain'], [112, 'Xibalba', 'Return of the Zotz'],
    [113, 'Ctis', 'Desert Tombs'], [115, 'Midgard', 'Age of Men'], [116, 'Bogarus', 'Age of Heroes'],
    [117, 'Utgard', 'Well of Urd'], [118, 'Vaettiheim', 'Wolf Kin Jarldom'], [119, 'Feminie', 'Sage-Queens'],
    [120, 'Piconye', 'Legacy of the Prester King'], [121, 'Andramania', 'Dog Republic'],
    [123, 'Pyrene', 'Demon Knights'],
    [125, 'Erytheia', 'Kingdom of Two Worlds'], [126, 'Atlantis', 'Frozen Sea'], [127, 'Rlyeh', 'Dreamlands']
]

OTHER_NATIONS = [
    [0, 'Independents', 'Normal Independents'],
    [2, 'Special Independents', 'e.g. Horrors'],
    [4, 'Roaming Independents', 'e.g. Barbarians']
]

ALL_NATIONS = EA_NATIONS + MA_NATIONS + LA_NATIONS
AGE_NATIONS = [EA_NATIONS, MA_NATIONS, LA_NATIONS]

VICTORY_CONDITIONS = [
    [0, 'Standard', 'Nothing'], [2, 'Dominion', 'Dominion score req.'],
    [3, 'Provinces', 'Provinces required'], [4, 'Research', 'Research points req.'],
    [6, 'Thrones', 'Nbr of Ascension Points']
]

POPTYPES = [
    [25, 'Barbarians'], [26, 'Horse Tribe'], [27, 'Militia, Archers, Hvy Inf'],
    [28, 'Militia, Archers, Hvy Inf'], [29, 'Militia, Archers, Hvy Inf'],
    [30, 'Militia, Longbow, Knight'], [31, 'Tritons'], [32, 'Lt Inf, Hvy Inf, X-Bow'],
    [33, 'Lt Inf, Hvy Inf, X-Bow'], [34, 'Raptors'], [35, 'Slingers'], [36, 'Lizards'],
    [37, 'Woodsmen'], [38, 'Hoburg'], [39, 'Militia, Archers, Lt Inf'], [40, 'Amazon, Crystal'],
    [41, 'Amazon, Garnet'], ['42', 'Amazon, Jade'], ['43', 'Amazon, Onyx'], [44, 'Troglodytes'],
    [45, 'Tritons, Shark Knights'], [46, 'Amber Clan Tritons'], [47, 'X-Bow, Hvy Cavalry'],
    [48, 'Militia, Lt Inf, Hvy Inf'], [49, 'Militia, Lt Inf, Hvy Inf'],
    [50, 'Militia, Lt Inf, Hvy Inf'], [51, 'Militia, Lt Cav, Hvy Cav'],
    [52, 'Militia, Lt Cav, Hvy Cav'], [53, 'Militia, Lt Cav, Hvy Cav'], [54, 'Hvy Inf, Hvy Cavalry'],
    [55, 'Hvy Inf, Hvy Cavalry'], [56, 'Hvy Inf, Hvy Cavalry'], [57, 'Shamblers'],
    [58, 'Lt Inf, Hvy Inf, X-Bow'], [59, 'Militia, Lt Inf, Archers'], [60, 'Militia, Lt Inf, Archers'],
    [61, 'Vaettir, Trolls'], [62, 'Tribals, Deer'], [63, 'Tritons'], [64, 'Tritons'],
    [65, 'Ichtyids'], [66, 'Vaettir'], [67, 'Vaettir, Dwarven Smith'],
    [68, 'Slingers, Hvy Inf, Elephants'], [69, 'Asmeg'], [70, 'Vaettir, Svartalf'], [71, 'Trolls'],
    [72, 'Mermen'], [73, 'Tritons, Triton Knights'], [74, 'Lt Inf, Lt Cav, Cataphracts'],
    [75, 'Hoburg, LA'], [76, 'Hoburg, EA'], [77, 'Atavi Apes'], [78, 'Tribals, Wolf'],
    [79, 'Tribals, Bear'], [80, 'Tribals, Lion'], [81, 'Pale Ones'], [82, 'Tribals, Jaguar'],
    [83, 'Tribals, Toad'], [84, 'Cavemen'], [85, 'Kappa'], [86, 'Bakemono'], [87, 'Bakemono'],
    [88, 'Ko-Oni'], [89, 'Fir Bolg'], [90, 'Turtle Tribe Tritons'], [91, 'Shark Tribe Tritons'],
    [92, 'Shark Tribe, Shark Riders'], [93, 'Zotz'], [94, 'Lava-born'], [95, 'Ichtyid Shaman'],
    [96, 'Bone Tribe'], [97, 'Merrow'], [98, 'Kulullu'], [99, 'Bronze Hoplites'], [100, 'Bronze Hvy Inf'],
    [101, 'Bronze Hvy Cav, Hvy Inf'], [102, 'Bronze Hvy Spear'], [103, 'Cynocephalians'], [104, 'Bekrydes'],
    [105, 'Wet Ones'], [106, 'Nexus']
]

FORT = [
    [1, 'Palisades'], [2, 'Fortress'], [3, 'Castle'], [4, 'Citadel'], [5, 'Rock Walls'],
    [6, 'Fortress'], [7, 'Castle'], [8, 'Castle of Bronze and Crystal'], [9, 'Kelp Fort'],
    [10, 'Bramble Fort'], [11, 'City Palisades'], [12, 'Walled City'], [13, 'Fortified City'],
    [14, 'Great Walled City'], [15, 'Giant Palisades'], [16, 'Giant Fortress'], [17, 'Giant Castle'],
    [18, 'Giant Citadel'], [19, 'Grand Citadel'], [20, 'Ice Walls'], [21, 'Ice Fortress'],
    [22, 'Ice Castle'], [23, 'Ice Citadel'], [24, 'Wizards Tower'], [25, 'Citadel of Power'],
    [27, 'Fortified village'], [28, 'Wooden Fort'], [29, 'Crystal Citadel']
]

SPECIAL_NEIGHBOUR = [
    [0, 'Standard border'], [33, 'Mountain pass'], [2, 'River border'], [4, 'Impassable'], [8, 'Road'],
    [16, 'River bridge'], [36, 'Impassable mountain'], [3, 'Waterfalls']
]
