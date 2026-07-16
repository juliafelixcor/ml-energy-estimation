# Como executar

## 1. Criar ambiente virtual

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Linux/Mac

```bash
source .venv/bin/activate
```

---

## 2. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 3. Executar

Treinamento

```bash
python main.py --stage train
```

Inferência

```bash
python main.py --stage inference
```

Os dois

```bash
python main.py
```

---

# Métricas coletadas

Durante a execução do modelo, o sistema realiza amostragens periódicas das métricas de hardware.

Os resultados são armazenados automaticamente em:

```text
output/train_metrics_database.csv
```

ou

```text
output/inference_metrics_database.csv
```

---

# Descrição das colunas

| Coluna           | Descrição                                           |
| ---------------- | --------------------------------------------------- |
| execution_time_s | Tempo total de execução (segundos)                  |
| avg_cpu_%        | Utilização média da CPU (%)                         |
| max_cpu_%        | Maior utilização da CPU (%)                         |
| avg_ram_%        | Utilização média da memória RAM (%)                 |
| avg_gpu_%        | Utilização média da GPU (%)                         |
| max_gpu_%        | Maior utilização da GPU (%)                         |
| avg_vram_%       | Utilização média da memória de vídeo (VRAM) (%)     |
| avg_power_W      | Potência média da GPU durante a execução (Watts)    |
| total_energy_J   | Energia total consumida durante a execução (Joules) |
| model_name       | Nome do modelo executado                            |
| stage            | Etapa executada (train ou inference)                |
| device_used      | Dispositivo utilizado (cpu ou cuda)                 |

---

# Como cada métrica é obtida

## Tempo de execução

Biblioteca utilizada:

```text
time
```

Calculado por:

```python
execution_time = end_time - start_time
```

---

## CPU

Biblioteca:

```text
psutil
```

Funções utilizadas:

```python
psutil.cpu_percent()
```

São calculados:

* utilização média;
* utilização máxima.

---

## Memória RAM

Biblioteca:

```text
psutil
```

Função utilizada:

```python
psutil.virtual_memory().percent
```

É armazenada a utilização média da memória principal.

---

## GPU

Biblioteca:

```text
pynvml
```

Funções utilizadas:

* utilização da GPU;
* utilização da VRAM;
* potência instantânea.

A partir das leituras periódicas são calculados:

* utilização média;
* utilização máxima;
* potência média.

---

## Energia total

Quando uma GPU NVIDIA está disponível, a energia é estimada por:

[
E=P_{médio}\times t
]

onde

* (P_{médio}) é a potência média (Watts);
* (t) é o tempo de execução (segundos).

O resultado é expresso em Joules (J).

Caso o experimento seja executado apenas em CPU, a biblioteca `pynvml` não consegue obter a potência do processador. Nesse cenário, os campos relacionados à potência e energia permanecem iguais a zero, indicando ausência de medição e não ausência de consumo energético.
