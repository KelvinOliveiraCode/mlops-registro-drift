"""Testes do DriftDetector — estatística pura (sem Evidently)."""

from __future__ import annotations

import pytest

from mlops_registro_drift.drift import DriftDetector


def test_sem_drift_quando_medias_iguais():
    detector = DriftDetector(threshold=0.1)
    referencia = {"x": [1.0, 2.0, 3.0]}
    atual = {"x": [1.0, 2.0, 3.0]}

    relatorio = detector.detect(referencia, atual)

    assert relatorio.drift_detected is False
    assert relatorio.n_drifted == 0
    assert relatorio.results[0].drift_detected is False


def test_drift_quando_desvio_excede_limiar():
    detector = DriftDetector(threshold=0.1)
    referencia = {"x": [10.0, 10.0, 10.0]}
    atual = {"x": [20.0, 20.0, 20.0]}  # desvio relativo 1.0 > 0.1

    relatorio = detector.detect(referencia, atual)

    assert relatorio.drift_detected is True
    assert relatorio.n_drifted == 1
    assert relatorio.results[0].drift_detected is True
    assert relatorio.results[0].method == "mean_deviation"


def test_sem_drift_abaixo_do_limiar():
    detector = DriftDetector(threshold=0.5)
    referencia = {"x": [10.0, 10.0, 10.0]}
    atual = {"x": [14.0, 14.0, 14.0]}  # desvio relativo 0.4 < 0.5

    relatorio = detector.detect(referencia, atual)

    assert relatorio.drift_detected is False
    assert relatorio.n_drifted == 0


def test_limiar_zero_detecta_qualquer_diferenca():
    detector = DriftDetector(threshold=0.0)
    relatorio = detector.detect({"x": [1.0]}, {"x": [2.0]})
    assert relatorio.drift_detected is True


def test_coluna_vazia_media_zero_sem_erro():
    detector = DriftDetector(threshold=0.1)
    relatorio = detector.detect({"x": []}, {"x": [5.0]})
    assert relatorio.results[0].reference_mean == 0.0
    assert relatorio.results[0].drift_detected is True


def test_resultados_ordenados_por_coluna():
    detector = DriftDetector(threshold=0.1)
    referencia = {"b": [1.0], "a": [1.0]}
    atual = {"b": [1.0], "a": [100.0]}

    relatorio = detector.detect(referencia, atual)

    colunas = [resultado.column for resultado in relatorio.results]
    assert colunas == ["a", "b"]


def test_threshold_negativo_erra():
    with pytest.raises(ValueError):
        DriftDetector(threshold=-0.1)
