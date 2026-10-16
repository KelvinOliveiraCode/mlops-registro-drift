"""Testes do ModelRegistry — backend local (sem MLflow, sem Docker)."""

from __future__ import annotations

from mlops_registro_drift.registry import FIXED_CLOCK, ModelEntry, ModelRegistry


def test_registro_cria_versao_um_com_metricas_e_origem_local(tmp_path, fixed_clock):
    caminho = tmp_path / "registro.json"
    registro = ModelRegistry(path=caminho, clock=fixed_clock, use_mlflow=False)

    entrada = registro.register(
        "modelo-x", object(), metrics={"acuracia": 0.92}, stage="Staging"
    )

    assert isinstance(entrada, ModelEntry)
    assert entrada.name == "modelo-x"
    assert entrada.version == "1"
    assert entrada.stage == "Staging"
    assert entrada.metrics == {"acuracia": 0.92}
    assert entrada.source == "local"
    assert entrada.created_at == FIXED_CLOCK

    ultimo = registro.get_latest("modelo-x")
    assert ultimo is not None
    assert ultimo.version == "1"
    assert registro.list_models() == ["modelo-x"]


def test_registro_segunda_versao_incrementa_numero(tmp_path, fixed_clock):
    caminho = tmp_path / "registro.json"
    registro = ModelRegistry(path=caminho, clock=fixed_clock, use_mlflow=False)

    registro.register("modelo-y", object())
    entrada_v2 = registro.register("modelo-y", object(), stage="Production")

    assert entrada_v2.version == "2"
    assert registro.get_latest("modelo-y").version == "2"


def test_get_latest_retorna_none_quando_nao_existe(tmp_path, fixed_clock):
    registro = ModelRegistry(
        path=tmp_path / "registro.json", clock=fixed_clock, use_mlflow=False
    )
    assert registro.get_latest("inexistente") is None
    assert registro.list_models() == []


def test_transition_stage_muda_estagio_e_persiste(tmp_path, fixed_clock):
    caminho = tmp_path / "registro.json"
    registro = ModelRegistry(path=caminho, clock=fixed_clock, use_mlflow=False)
    registro.register("modelo-z", object())

    atualizado = registro.transition_stage("modelo-z", "1", "Archived")

    assert atualizado is not None
    assert atualizado.stage == "Archived"
    assert registro.get_latest("modelo-z").stage == "Archived"

    recarregado = ModelRegistry(path=caminho, clock=fixed_clock, use_mlflow=False)
    assert recarregado.get_latest("modelo-z").stage == "Archived"


def test_transition_stage_versao_inexistente_retorna_none(tmp_path, fixed_clock):
    registro = ModelRegistry(
        path=tmp_path / "registro.json", clock=fixed_clock, use_mlflow=False
    )
    assert registro.transition_stage("qualquer", "99", "Production") is None


def test_registro_usa_fixed_clock_eh_deterministico(tmp_path, fixed_clock):
    caminho = tmp_path / "registro.json"
    r1 = ModelRegistry(path=caminho, clock=fixed_clock, use_mlflow=False)
    r1.register("m", object())
    r2 = ModelRegistry(path=caminho, clock=fixed_clock, use_mlflow=False)
    assert r2.get_latest("m").created_at == FIXED_CLOCK
