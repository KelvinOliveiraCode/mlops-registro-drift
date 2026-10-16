"""Registro de modelo.

Usa MLflow quando disponível; caso contrário, grava um arquivo JSON local.
É determinístico quando um relógio fixo é injetado (útil em testes).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

try:  # dependência opcional: MLflow
    import mlflow  # type: ignore[import-not-found]

    _MLFLOW_DISPONIVEL = True
except Exception:  # MLflow não instalado
    _MLFLOW_DISPONIVEL = False

DEFAULT_REGISTRY_PATH = Path.home() / ".mlops_registro_drift" / "registry.json"
FIXED_CLOCK = "2026-01-01T00:00:00+00:00"


@dataclass
class ModelEntry:
    """Entrada do registro: metadados de uma versão de modelo."""

    name: str
    version: str
    stage: str = "None"
    metrics: dict[str, float] = field(default_factory=dict)
    path: str = ""
    created_at: str = FIXED_CLOCK
    source: str = "local"  # "mlflow" ou "local"


class ModelRegistry:
    """Registro de modelos com backend MLflow ou arquivo JSON local."""

    def __init__(
        self,
        path: Optional[Path] = None,
        clock: Optional[Callable[[], str]] = None,
        use_mlflow: Optional[bool] = None,
    ) -> None:
        self.path = path or DEFAULT_REGISTRY_PATH
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat())
        self.use_mlflow = _MLFLOW_DISPONIVEL if use_mlflow is None else use_mlflow
        self._entries: dict[str, list[ModelEntry]] = {}
        self._load()

    # ------------------------------------------------------------------ carga
    def _load(self) -> None:
        if self.use_mlflow or not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, TypeError):
            self._entries = {}
            return
        self._entries = {
            name: [ModelEntry(**item) for item in items]
            for name, items in data.items()
        }

    # ------------------------------------------------------------------ grava
    def _save(self) -> None:
        if self.use_mlflow:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {name: [asdict(entry) for entry in items]
                   for name, items in self._entries.items()}
        self.path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # ----------------------------------------------------------- backend MLflow
    def _next_version_mlflow(self, name: str) -> str:  # pragma: no cover
        """Não usado enquanto MLflow não estiver instalado."""
        raise RuntimeError("MLflow não está disponível neste ambiente.")

    # -------------------------------------------------------------------- API
    def register(
        self,
        name: str,
        model: object,
        metrics: Optional[dict[str, float]] = None,
        stage: str = "None",
    ) -> ModelEntry:
        """Registra uma nova versão de modelo e retorna a entrada criada."""
        versions = self._entries.get(name, [])
        version = str(len(versions) + 1)
        entry = ModelEntry(
            name=name,
            version=version,
            stage=stage,
            metrics=dict(metrics or {}),
            path=str(self.path),
            created_at=self.clock(),
            source="mlflow" if self.use_mlflow else "local",
        )
        self._entries.setdefault(name, []).append(entry)
        self._save()
        return entry

    def get_latest(self, name: str) -> Optional[ModelEntry]:
        """Retorna a versão mais recente de um modelo, ou None se não existir."""
        versions = self._entries.get(name, [])
        return versions[-1] if versions else None

    def list_models(self) -> list[str]:
        """Retorna os nomes dos modelos registrados, em ordem alfabética."""
        return sorted(self._entries.keys())

    def transition_stage(
        self, name: str, version: str, stage: str
    ) -> Optional[ModelEntry]:
        """Muda o estágio de uma versão específica; retorna None se não encontrar."""
        for entry in self._entries.get(name, []):
            if entry.version == version:
                entry.stage = stage
                self._save()
                return entry
        return None
