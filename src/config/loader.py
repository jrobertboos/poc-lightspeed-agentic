"""YAML configuration file loader."""

from pathlib import Path

import yaml

from src.config.models import AppConfig


def load_config(path: str | Path = "config.yaml") -> AppConfig:
    """Load and validate application configuration from a YAML file."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        data = yaml.safe_load(f)

    return AppConfig.model_validate(data)
