"""Module registry — registration + capability discovery (L2)."""

from __future__ import annotations

from typing import Iterable

from .module import Module


class ModuleRegistry:
    def __init__(self):
        self._modules: dict[str, Module] = {}

    def register(self, module: Module) -> None:
        if not module.id:
            raise ValueError("module must have a non-empty id")
        if module.id in self._modules:
            raise ValueError(f"duplicate module id: {module.id}")
        self._modules[module.id] = module

    def get(self, module_id: str) -> Module:
        if module_id not in self._modules:
            raise KeyError(f"no such module: {module_id}")
        return self._modules[module_id]

    def list_modules(self) -> list[dict]:
        return [
            {"id": m.id, "name": m.name, "line": m.line, "version": m.version,
             "state": m.state().value, "backing_doi": m.backing.doi if m.backing else None}
            for m in self._modules.values()
        ]

    def by_line(self, line: str) -> Iterable[Module]:
        return (m for m in self._modules.values() if m.line == line)

    def __len__(self) -> int:
        return len(self._modules)
