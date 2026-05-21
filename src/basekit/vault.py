"""TOML-backed local secret/config vault helper."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Vault:
    """Read values from a local TOML vault file."""

    vault_toml_file_path: str | Path | None = field(default=None, repr=False)

    def get(self, name: str | None = None) -> Any:
        data = self.load()
        if name:
            return data[name]
        return data

    def load(self) -> dict[str, Any]:
        if self.vault_toml_file_path is None:
            raise ValueError("vault_toml_file_path is required")
        with Path(self.vault_toml_file_path).open("rb") as vault_file:
            return tomllib.load(vault_file)
