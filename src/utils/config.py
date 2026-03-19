"""
config.py — load settings.yaml and .env in one place.

Usage:
    from src.utils.config import load_config
    cfg = load_config()
    print(cfg["embedding"]["model"])
"""

from pathlib import Path
import os
import yaml
from dotenv import load_dotenv

# The repo root is two levels above this file (src/utils/config.py → ../../)
REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "settings.yaml"
ENV_PATH = REPO_ROOT / ".env"


def load_config(config_path: Path = CONFIG_PATH) -> dict:
    """
    Load settings.yaml and .env, then return the config dict.

    Environment variables from .env are loaded into os.environ so that
    API keys can be accessed via os.getenv() throughout the codebase.
    """
    # Load .env if it exists (won't raise if missing)
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)

    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    return cfg
