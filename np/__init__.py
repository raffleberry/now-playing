import os
import pathlib

import np.icons  # noqa: F401

CONFIG_DIR = pathlib.Path.home() / ".raffleberry" / "now-playing"
CONFIG_FILE = CONFIG_DIR / "config.json"
ROOT_DIR = pathlib.Path.cwd()
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DEV = bool(os.getenv("DEV", False))

