import sys
import types

gui_mod = types.ModuleType("DreamAtlas.GUI")
gui_mod.__path__ = []
gui_mod.run_interface = lambda: None
sys.modules["DreamAtlas.GUI"] = gui_mod
for sub in ["main_interface", "widgets", "loading", "ui_data"]:
    sys.modules[f"DreamAtlas.GUI.{sub}"] = types.ModuleType(f"DreamAtlas.GUI.{sub}")
