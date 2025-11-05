import os
import pathlib


def generate_icons():
    pkg_dir = pathlib.Path(__file__).parent / ".."
    resources_src = pkg_dir / "resources" / "icons.qrc"
    resources_dst = pkg_dir / "np" / "icons.py"
    os.system(f'pyside6-rcc "{resources_src}" -o "{resources_dst}"')

if __name__ == "__main__":
    generate_icons()