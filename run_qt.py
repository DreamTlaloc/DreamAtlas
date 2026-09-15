from DreamAtlas.GUI import run_interface
# import cProfile

if __name__ == "__main__":  # This is what runs in the .exe loading up the main interface which contains all the DreamAtlas functionality
    run_interface()

# import sys
# import os
# import pathlib
# import traceback

# try:
#     # if getattr(sys, 'frozen', False):
#     #     exe_dir = pathlib.Path(sys.executable).parent
#     #     internal_dir = exe_dir / '_internal'
#     #     os.chdir(str(exe_dir))
#     #
#     #     # Add llvmlite binding dir so ctypes can find llvmlite.dll
#     #     llvmlite_binding = internal_dir / 'llvmlite' / 'binding'
#     #     os.add_dll_directory(str(llvmlite_binding))
#     #     os.add_dll_directory(str(internal_dir))
#     #     os.environ['PATH'] = str(llvmlite_binding) + os.pathsep + str(internal_dir) + os.pathsep + os.environ.get(
#     #         'PATH', '')
#     #
#     #     plugin_dir = internal_dir / 'PyQt5' / 'Qt5' / 'plugins'
#     #     os.environ['QT_PLUGIN_PATH'] = str(plugin_dir)
#     #     os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = str(plugin_dir / 'platforms')
#
#     log = open(pathlib.Path(sys.executable).parent / 'startup.log', 'w')
#     log.write('step 1: env set\n')
#     log.flush()
#
#     log.write('step 3: backend set\n')
#     log.flush()
#
#     log.write('step 5: PyQt5 imported\n')
#     log.flush()
#
#     from DreamAtlas.GUI import run_interface
#     log.write('step 6: DreamAtlas imported\n')
#     log.flush()
#
#     log.close()
#
#     if __name__ == '__main__':
#         run_interface()
#
# except Exception:
#     try:
#         log.write('FAILED\n'); log.flush()
#         log.close()
#     except:
#         pass
#     error_path = pathlib.Path(sys.executable).parent / 'error.log'
#     with open(error_path, 'w') as f:
#         traceback.print_exc(file=f)