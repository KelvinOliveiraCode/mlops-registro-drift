"""mlops-registro-drift: registro de modelo + detecção de drift de dados.

MVP de MLOps com:
- Registro de modelo (MLflow quando disponível, senão arquivo JSON local).
- Detecção de drift de dados (Evidently quando disponível, senão teste
  estatístico simples de desvio de média).

Tudo é determinístico quando um relógio fixo é injetado, e os testes não
dependem de MLflow, Evidently nem Docker.
"""

from .drift import DriftDetector, DriftReport, DriftResult
from .pipeline import PipelineReport, SimpleModel, run_pipeline
from .registry import ModelEntry, ModelRegistry

__all__ = [
    "DriftDetector",
    "DriftReport",
    "DriftResult",
    "ModelEntry",
    "ModelRegistry",
    "PipelineReport",
    "SimpleModel",
    "run_pipeline",
]

__version__ = "0.1.0"
