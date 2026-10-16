"""CLI: executa o pipeline de demonstração com dados sintéticos."""

from __future__ import annotations

from .pipeline import run_pipeline


def _dados_sinteticos() -> tuple[dict[str, list[float]], dict[str, list[float]]]:
    reference = {
        "feature_a": [1.0, 2.0, 3.0, 4.0, 5.0],
        "feature_b": [10.0, 12.0, 11.0, 13.0, 12.0],
    }
    current = {
        "feature_a": [1.1, 2.1, 2.9, 4.1, 5.1],
        "feature_b": [10.0, 12.0, 11.0, 13.0, 12.0],
    }
    return reference, current


def main() -> int:
    reference, current = _dados_sinteticos()
    relatorio = run_pipeline(reference, current, model_name="modelo-demo")
    print("Pipeline mlops-registro-drift executado com sucesso.")
    print(
        f"Modelo: {relatorio.model_name} v{relatorio.model_version} "
        f"({relatorio.model_source})"
    )
    print(
        f"Drift detectado: {relatorio.drift.drift_detected} "
        f"({relatorio.drift.n_drifted}/{relatorio.drift.n_columns} colunas)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
