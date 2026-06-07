from DreamAtlas import *
from pathlib import Path

PATH = Path('.').absolute()
name = 'test_map'
index = 1
# Load config
settings = DreamAtlasSettings(index)
settings.load_file(filename=PATH / 'examples' / '12_player_ea_test.dream')

smackdown_map = generator_dreamatlas(settings=settings)

# Make the files, default location is $REPO_DIR/maps/$NAME
smackdown_map.map_title = [None, name, name+'_plane2']
smackdown_map.publish(location=None, name=name)


# Plot map images (broken)
#smackdown_map.layout.plot() #TODO: fix this?
#smackdown_map.plot()
#plt.show()
