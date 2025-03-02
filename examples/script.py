from DreamAtlas import *

PATH = r'C:\Users\amyau\PycharmProjects\mapTlaloc\DreamAtlas\examples\\'
name = 'smackdown_2_finals6'
index = 1

# Load config
settings = DreamAtlasSettings(index)
settings.load_file(filename=PATH+'smackdown_2_finals.dream')

# cProfile.run('DreamAtlasGenerator(settings=settings)', sort='cumulative')
smackdown_map = generator_dreamatlas(settings=settings)

# Make the files
# smackdown_map.map_title = [None, name, name+'_plane2']
# smackdown_map.publish(location=PATH, name=name)

# Plot map images
smackdown_map.layout.plot()
# smackdown_map.plot()
plt.show()
