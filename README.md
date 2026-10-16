# mlops-registro-drift

Registro de modelo + detecção de drift de dados.

MVP de MLOps: registro de versão de modelo (MLflow quando disponível, senão arquivo JSON local) e detecção de drift de dados (Evidently quando disponível, senão teste estatístico simples de desvio de média). Tudo em Python, determinístico, sem dependências externas obrigatórias para rodar os testes.

## Português

### O que faz
- Registro de modelo: grava nome, versão, estágio, métricas e data de criação. Usa MLflow se instalado; caso contrário grava um arquivo JSON local (`~/.mlops_registro_drift/registry.json`).
- Detecção de drift: compara a média de cada coluna numérica entre dados de referência e dados atuais. Marca drift quando o desvio relativo excede o limiar (padrão 0,10). Usa Evidently se instalado; caso contrário aplica teste estatístico puro.
- Pipeline: ajusta um modelo determinístico (média de treino, `random_state=42`), registra a versão e executa a detecção de drift, retornando um relatório.

### Como usar
Requisitos: Python 3.10+.

```
python -m pip install -e .
python -m mlops_registro_drift
```

Saída esperada:

```
Pipeline mlops-registro-drift executado com sucesso.
Modelo: modelo-demo v1 (local)
Drift detectado: False (0/1 colunas)
```

### Testes
Executa a suíte pytest (sem MLflow, Evidently nem Docker):

```
python -m pytest -q
```

Resultado: 19 testes passando.

### Docker
```
docker build -t mlops-registro-drift .
docker run --rm mlops-registro-drift
```

### Licença
MIT.

### Autor
Kelvin Oliveira.

## English

### What it does
- Model registry: records name, version, stage, metrics and creation date. Uses MLflow if installed; otherwise writes a local JSON file (`~/.mlops_registro_drift/registry.json`).
- Data drift detection: compares the mean of each numeric column between reference and current data. Flags drift when relative deviation exceeds the threshold (default 0.10). Uses Evidently if installed; otherwise applies a pure statistical mean-deviation test.
- Pipeline: fits a deterministic model (training mean, `random_state=42`), registers the version and runs drift detection, returning a report.

### How to use
Requirements: Python 3.10+.

```
python -m pip install -e .
python -m mlops_registro_drift
```

Expected output:

```
Pipeline mlops-registro-drift executed successfully.
Model: modelo-demo v1 (local)
Drift detected: False (0/1 columns)
```

### Tests
Run the pytest suite (no MLflow, Evidently or Docker required):

```
python -m pytest -q
```

Result: 19 tests passing.

### Docker
```
docker build -t mlops-registro-drift .
docker run --rm mlops-registro-drift
```

### License
MIT.

### Author
Kelvin Oliveira.
