# BRIEF — mlops-registro-drift

Projeto de área IA/ML: registro de modelo + detecção de drift de dados (MVP).
Stack: Python, MLflow (opcional), Evidently (opcional), Docker.
Owner da validação: workflow manager.

## Entregas (arquivos criados)

Caminho base: `C:\Users\Kelvin\AppData\Local\Temp\opencode\github-staging\projects\mlops-registro-drift\`

| Arquivo | Função |
|---------|--------|
| `pyproject.toml` | Metadados do projeto, dependências opcionais (mlflow/evidently/dev), entry point CLI, config do pytest (`pythonpath = ["src"]`). |
| `Dockerfile` | Imagem Python 3.12-slim que instala o pacote e roda o pipeline. |
| `src/mlops_registro_drift/__init__.py` | Exporta a API pública e a versão. |
| `src/mlops_registro_drift/registry.py` | `ModelRegistry` (MLflow ou JSON local) + `ModelEntry`. Determinístico com relógio injetável. |
| `src/mlops_registro_drift/drift.py` | `DriftDetector` (Evidently ou desvio de média puro) + `DriftResult`/`DriftReport`. |
| `src/mlops_registro_drift/pipeline.py` | `SimpleModel` (random_state=42), `PipelineReport`, `run_pipeline()`. |
| `src/mlops_registro_drift/__main__.py` | CLI de demonstração com dados sintéticos. |
| `tests/__init__.py` | Marca o pacote de testes. |
| `tests/conftest.py` | Fixture `fixed_clock` para testes determinísticos. |
| `tests/test_registry.py` | Registro, versão, estágio, persistência, relógio fixo. |
| `tests/test_drift.py` | Detecção de drift, limiar, coluna vazia, ordenação, erro de limiar negativo. |
| `tests/test_pipeline.py` | Modelo determinístico, pipeline completo, detecção de drift, versão incremental, entradas vazias. |
| `README.md` | Documentação completa bilíngue PT-BR + EN (título, descrição, como usar, testes, licença MIT, autor). |
| `BRIEF.md` | Este resumo de entregas e como verificar. |

## Comando de teste usado

Executado a partir da raiz do projeto:

```
python -m pytest -q
```

## Resultado dos testes

`19 passed in 0.13s` — todos os testes passam (sem MLflow, Evidently nem Docker instalados; backend local e estatística pura).

## Caminhos

- README: `C:\Users\Kelvin\AppData\Local\Temp\opencode\github-staging\projects\mlops-registro-drift\README.md`
- BRIEF: `C:\Users\Kelvin\AppData\Local\Temp\opencode\github-staging\projects\mlops-registro-drift\BRIEF.md`

## Como verificar

1. Entre na pasta do projeto.
2. Rode `python -m pytest -q` → deve reportar `19 passed`.
3. Rode `python -m mlops_registro_drift` → deve imprimir o relatório do pipeline com `Drift detectado: False`.
4. (Opcional) `docker build -t mlops-registro-drift .` e `docker run --rm mlops-registro-drift` exigem Docker instalado.

Autor: Kelvin Oliveira. Licença: MIT.
