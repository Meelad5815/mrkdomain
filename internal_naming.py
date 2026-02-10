from __future__ import annotations

import json
import re
from pathlib import Path
from threading import Lock
from typing import Dict, Optional

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*\.(?:mrk|milaad)$")


class InternalNameService:
    """Stores and resolves private ecosystem names such as shop.mrk."""

    def __init__(self, store_path: str = "data/names.json") -> None:
        self.store_path = Path(store_path)
        self._lock = Lock()
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self._write({})

    def register(self, name: str, target: str) -> None:
        normalized = self._normalize_name(name)
        if not target or not target.strip():
            raise ValueError("target must not be empty")

        with self._lock:
            data = self._read()
            data[normalized] = target.strip()
            self._write(data)

    def resolve(self, name: str) -> Optional[str]:
        normalized = self._normalize_name(name)
        data = self._read()
        return data.get(normalized)

    def all_names(self) -> Dict[str, str]:
        return self._read()

    def _normalize_name(self, name: str) -> str:
        if not name:
            raise ValueError("name is required")

        normalized = name.strip().lower()
        if not NAME_PATTERN.match(normalized):
            raise ValueError(
                "name must look like shop.mrk or user.milaad and only use a-z, 0-9, . or -"
            )
        return normalized

    def _read(self) -> Dict[str, str]:
        if not self.store_path.exists():
            return {}
        return json.loads(self.store_path.read_text(encoding="utf-8"))

    def _write(self, payload: Dict[str, str]) -> None:
        self.store_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
