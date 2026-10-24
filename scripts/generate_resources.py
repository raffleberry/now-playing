"""Compile the Qt Designer UI files and the Qt resource bundle.

Run this after editing anything in ``np/ui/*.ui`` or ``resources/``:

    uv run python scripts/generate_resources.py
"""

import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def find_tool(name: str) -> str:
    """Find a PySide6 tool, preferring the one next to the active Python."""
    exe = f"{name}.exe" if sys.platform == "win32" else name
    local = pathlib.Path(sys.executable).parent / exe
    if local.exists():
        return str(local)

    found = shutil.which(name) or shutil.which(exe)
    if found:
        return found

    raise FileNotFoundError(
        f"Could not find '{name}'. Install the project dependencies with 'uv sync'."
    )


def compile_ui() -> None:
    """Generate ``np/ui/ui_<name>.py`` from each ``np/ui/<name>.ui``."""
    ui_dir = ROOT / "np" / "ui"
    uic = find_tool("pyside6-uic")
    for src in sorted(ui_dir.glob("*.ui")):
        dst = ui_dir / f"ui_{src.stem}.py"
        subprocess.run([uic, str(src), "-o", str(dst)], check=True)
        print(f"ui      {src.name} -> {dst.relative_to(ROOT)}")


def generate_icons() -> None:
    """Embed the icons and stylesheet from ``resources/icons.qrc``."""
    qrc = ROOT / "resources" / "icons.qrc"
    dst = ROOT / "np" / "icons.py"
    rcc = find_tool("pyside6-rcc")
    subprocess.run([rcc, str(qrc), "-o", str(dst)], check=True)
    print(f"resources {qrc.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")


def main() -> None:
    compile_ui()
    generate_icons()


if __name__ == "__main__":
    main()
