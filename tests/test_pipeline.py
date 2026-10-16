"""Testes do pipeline — sem MLflow, Evidently nem Docker."""

from __future__ import annotations

import pytest

from mlops_registro_drift.pipeline import PipelineReport, SimpleModel, run_pipeline


def test_simple_model_deterministico_com_random_state_fixo():
    valores = [1.0, 2.0, 3.0, 4.0, 5.0]
    m1 = SimpleModel(random_state=42).fit(valores)
    m2 = SimpleModel(random_state=42).fit(valores)
    assert m1.mean_ == m2.mean_ == 3.0
    assert m1.predict([9.0, 8.0]) == [3.0, 3.0]


def test_pipeline_executa_e_retorna_relatorio_completo(tmp_path, fixed_clock):
    referencia = {"feature_a": [1.0, 2.0, 3.0, 4.0, 5.0]}
    atual = {"feature_a": [1.0, 2.0, 3.0, 4.0, 5.0]}

    relatorio = run_pipeline(
        referencia,
        atual,
        model_name="modelo-demo",
        registry_path=tmp_path / "reg.json",
        clock=fixed_clock,
    )

    assert isinstance(relatorio, PipelineReport)
    assert relatorio.status == "ok"
    assert relatorio.model_name == "modelo-demo"
    assert relatorio.model_version == "1"
    assert relatorio.model_stage == "None"
    assert relatorio.model_source == "local"
    assert "mean_prediction" in relatorio.model_metrics
    assert relatorio.drift.drift_detected is False


def test_pipeline_detecta_drift_entre_referencia_e_atual(tmp_path, fixed_clock):
    referencia = {"feature_a": [10.0, 10.0, 10.0]}
    atual = {"feature_a": [100.0, 100.0, 100.0]}

    relatorio = run_pipeline(
        referencia,
        atual,
        registry_path=tmp_path / "reg.json",
        clock=fixed_clock,
    )

    assert relatorio.drift.drift_detected is True
    assert relatorio.drift.n_drifted == 1


def test_pipeline_registro_incrementa_versao(tmp_path, fixed_clock):
    referencia = {"x": [1.0, 2.0]}
    atual = {"x": [1.0, 2.0]}

    run_pipeline(
        referencia,
        atual,
        model_name="m",
        registry_path=tmp_path / "reg.json",
        clock=fixed_clock,
    )
    relatorio2 = run_pipeline(
        referencia,
        atual,
        model_name="m",
        registry_path=tmp_path / "reg.json",
        clock=fixed_clock,
    )

    assert relatorio2.model_version == "2"


def test_pipeline_rejeita_referencia_vazia(tmp_path, fixed_clock):
    with pytest.raises(ValueError):
        run_pipeline(
            {},
            {"x": [1.0]},
            registry_path=tmp_path / "reg.json",
            clock=fixed_clock,
        )


def test_pipeline_rejeita_atual_vazio(tmp_path, fixed_clock):
    with pytest.raises(ValueError):
        run_pipeline(
            {"x": [1.0]},
            {},
            registry_path=tmp_path / "reg.json",
            clock=fixed_clock,
        )
