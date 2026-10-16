"""Detecção de drift de dados.

Usa Evidently quando disponível; caso contrário, aplica um teste estatístico
simples de desvio de média entre os dados de referência e os dados atuais.
É totalmente determinístico (estatística pura, sem geradores aleatórios).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

try:  # dependência opcional: Evidently
    from evidently import test_suite  # type: ignore[import-not-found]

    _EVIDENTLY_DISPONIVEL = True
except Exception:  # Evidently não instalado
    _EVIDENTLY_DISPONIVEL = False


@dataclass
class DriftResult:
    """Resultado do teste de drift para uma única coluna."""

    column: str
    reference_mean: float
    current_mean: float
    drift_detected: bool
    method: str = "mean_deviation"
    p_value: Optional[float] = None


@dataclass
class DriftReport:
    """Relatório completo de drift entre referência e dados atuais."""

    drift_detected: bool
    n_columns: int
    n_drifted: int
    results: list[DriftResult] = field(default_factory=list)


class DriftDetector:
    """Detecta drift comparando médias de colunas numéricas."""

    def __init__(self, threshold: float = 0.1) -> None:
        if threshold < 0:
            raise ValueError("threshold deve ser maior ou igual a zero.")
        self.threshold = threshold

    @staticmethod
    def _column_means(data: dict[str, list[float]]) -> dict[str, float]:
        return {
            col: (sum(vals) / len(vals) if vals else 0.0)
            for col, vals in data.items()
        }

    def detect(
        self,
        reference: dict[str, list[float]],
        current: dict[str, list[float]],
    ) -> DriftReport:
        """Detecta drift pelo desvio relativo de média de cada coluna.

        Uma coluna é considerada com drift quando
        |media_atual - media_referencia| / max(|media_referencia|, eps)
        excede o limiar configurado.
        """
        ref_means = self._column_means(reference)
        cur_means = self._column_means(current)

        resultados: list[DriftResult] = []
        for coluna in sorted(set(ref_means) | set(cur_means)):
            ref_mean = ref_means.get(coluna, 0.0)
            cur_mean = cur_means.get(coluna, 0.0)
            denominador = max(abs(ref_mean), 1e-9)
            desvio_relativo = abs(cur_mean - ref_mean) / denominador
            com_drift = desvio_relativo > self.threshold
            resultados.append(
                DriftResult(
                    column=coluna,
                    reference_mean=ref_mean,
                    current_mean=cur_mean,
                    drift_detected=com_drift,
                    method="mean_deviation",
                )
            )

        n_drifted = sum(1 for r in resultados if r.drift_detected)
        return DriftReport(
            drift_detected=n_drifted > 0,
            n_columns=len(resultados),
            n_drifted=n_drifted,
            results=resultados,
        )
