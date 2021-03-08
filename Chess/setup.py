import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
additional_modules = []

include_files = ['autorun.inf',"ChessEngine.py"]

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="SagaBot",
      version="0.1",
      description="Za Fanove",
      options={"build_exe": {'include_files':include_files}},
      executables=[Executable(script="ChessMain.py", base=base)])