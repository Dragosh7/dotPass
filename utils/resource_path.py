import os
import sys

def resource_path(relative_path: str) -> str:
    """
    Return the absolute path to a resource file, compatible with PyInstaller.
    It works both in dev mode and in bundled .exe (MEIPASS).
    """
    try:
        base_path = sys._MEIPASS  # Folder temporar folosit de PyInstaller
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
