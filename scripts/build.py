import pathlib
import subprocess

import generate_resources

src_dir = pathlib.Path(__file__).resolve().parent.parent


def main():
    generate_resources.main()

    pyinstaller = generate_resources.find_tool("pyinstaller")
    subprocess.run(
        [
            pyinstaller,
            f"--icon={src_dir / 'resources' / 'icons' / 'play.png'}",
            "--name=NowPlaying",
            "--noconfirm",
            "--noconsole",
            str(src_dir / "np" / "main.py"),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
