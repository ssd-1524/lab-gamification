import toml
from pathlib import Path

CONFIG_PATH = Path("config.toml")

def load_config():
    if not CONFIG_PATH.exists():
        raise RuntimeError("config.toml not found")

    return toml.load(CONFIG_PATH)
