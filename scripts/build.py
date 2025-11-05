import os
import pathlib

src_dir = pathlib.Path(__file__).parent.parent

def generate_icons():
    global src_dir
    resources_src = src_dir / "resources" / "icons.qrc"
    resources_dst = src_dir / "np" / "icons.py"
    os.system(f'pyside6-rcc "{resources_src}" -o "{resources_dst}"')


def main():
    global src_dir
    os.system(f'pyinstaller --icon="{src_dir}/resources/icons/play.png" --name="NowPlaying" --noconsole "{src_dir / "np" / "main.py" }"')

if __name__ == "__main__":
    generate_icons()
    main()