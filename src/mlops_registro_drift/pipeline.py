"""Pipeline de registro de modelo + detecção de drift de dados.

Orquestra: ajuste de um modelo determinístico, registro de versão e
detecção de drift entre dados de referência e dados atuais.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from .drift import DriftDetector, DriftReport
from .registry import ModelRegistry
from pathlib import Path


@dataclass
class SimpleModel:
    """Modelo determinístico: prediz a média de treino (random_state fixo)."""

    random_state: int = 42
    mean_: Optional[float] = None

    def fit(self, values: list[float]) -> "SimpleModel":
        """Ajusta a média de treino e retorna o próprio modelo."""
        self.mean_ = sum(values) / len(values) if values else 0.0
        return self

    def predict(self, values: list[float]) -> list[float]:
        """Prediz a média de treino para cada entrada."""
        if self.mean_ is None:
            raise ValueError("Modelo não foi ajustado. Chame fit() primeiro.")
        return [self.mean_ for _ in values]


@dataclass
class PipelineReport:
    """Relatório da execução do pipeline."""

    model_name: str
    model_version: str
    model_stage: str
    model_source: str
    model_metrics: dict[str, float] = field(default_factory=dict)
    drift: DriftReport = field(default_factory=DriftReport)
    status: str = "ok"


def _achar_coluna_alvo(
    reference: dict[str, list[float]], current: dict[str, list[float]]
) -> str:
    """Escolhe a primeira coluna comum (ou a primeira da referência) como alvo."""
    comuns = sorted(set(reference) & set(current))
    if comuns:
        return comuns[0]
    return sorted(reference.keys())[0] if reference else next(iter(current))


def run_pipeline(
    reference: dict[str, list[float]],
    current: dict[str, list[float]],
    model_name: str = "modelo-padrao",
    registry_path: Optional[Path] = None,
    clock: Optional[Callable[[], str]] = None,
    threshold: float = 0.1,
) -> PipelineReport:
    """Executa o pipeline completo e retorna o relatório.

    Passos:
      1. Ajusta SimpleModel nos valores da referência (random_state=42).
      2. Registra a versão do modelo no ModelRegistry (MLflow ou local).
      3. Detecta drift entre referência e dados atuais.
    """
    if not reference:
        raise ValueError("reference não pode estar vazio.")
    if not current:
        raise ValueError("current não pode estar vazio.")

    detector = DriftDetector(threshold=threshold)
    drift_report = detector.detect(reference, current)

    todos_valores = [v for coluna in reference.values() for v in coluna]
    modelo = SimpleModel(random_state=42).fit(todos_valores)
    metricas = {
        "mean_prediction": modelo.mean_,
        "n_reference": float(len(todos_valores)),
    }

    registro = ModelRegistry(path=registry_path, clock=clock)
    entrada = registro.register(
        name=model_name,
        model=modelo,
        metrics=metricas,
        stage="None",
    )

    return PipelineReport(
        model_name=entrada.name,
        model_version=entrada.version,
        model_stage=entrada.stage,
        model_source=entrada.source,
        model_metrics=entrada.metrics,
        drift=drift_report,
        status="ok",
    )
