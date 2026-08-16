from DreamAtlas.classes.class_map import DominionsMap


def test_load_map_with_special_neighbours():
    m = DominionsMap()
    m.load_folder("tests/assets")
    assert len(m.province_list[1]) == 4
    assert len(m.layout.special_neighbours[1]) == 2
    assert m.layout.special_neighbours[1][0] == [1, 3, 33]
    assert m.layout.special_neighbours[1][1] == [2, 4, 2]
