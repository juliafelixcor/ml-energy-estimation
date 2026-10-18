# Estimativa do consumo energético de modelos de ML

Implementação da proposta metodológica: executar treino e inferência de vários
modelos em diferentes configurações, medir o consumo de energia e montar uma
base de dados para treinar um modelo preditivo (regressão simbólica).

| Etapa da proposta            | Onde está no código                               |
| ---------------------------- | ------------------------------------------------- |
| 1. Definir experimentos      | `experiments/grids.py`                            |
| 2. Executar treinamento      | `stages/train.py` + `experiments/runner.py`       |
| 3. Executar inferência       | `stages/inference.py` + `experiments/runner.py`   |
| 4. Organizar dados           | `output/runs.csv` (uma linha por execução/etapa)  |
| 5. Treinar modelo preditivo  | *a fazer, depois da coleta*                       |
| 6. Analisar e aplicar        | *a fazer*                                         |

`analisar_resultados.py` e `analisar_matriz.py` resumem os experimentos
anteriores (LeNet5/MNIST), salvos no formato antigo em
`output/train_metrics_database.csv` e `output/inference_metrics_database.csv`.

---

# De onde vem a energia medida

O alvo do modelo preditivo precisa ser uma **medição real**. Estimativas por
TDP não servem, como mostra o artigo da H100: se o alvo for calculado por uma
fórmula, a regressão simbólica só vai redescobrir essa fórmula.

| Fonte (`energy_source`) | Onde                       | O que mede                                  |
| ----------------------- | -------------------------- | ------------------------------------------- |
| `battery_system`        | Notebook **fora da tomada** | Potência do notebook inteiro (taxa de descarga da bateria) |
| `nvml_gpu`              | Colab/Kaggle (GPU T4)      | Energia da GPU (sensor da placa)            |

A GPU do notebook (GeForce MX110) **não tem sensor de potência**, e o PyTorch
instalado nele é a versão só para CPU. Por isso:

* experimentos de **CPU** rodam no notebook, medidos pela bateria;
* experimentos de **GPU** rodam no Colab/Kaggle (`colab_gpu.ipynb`).

As colunas `cpu_energy_est_J` e `ram_energy_est_J` continuam sendo calculadas
(modelo linear: 3 W em repouso até 25 W em 100% de uso; 0,372 W por GB de RAM),
mas são **estimativas**, úteis só para comparar com a medição real.

### Cuidados com a medição

* O Windows atualiza a taxa de descarga a cada ~5–20 s. Por isso cada etapa é
  repetida até a janela de medição durar pelo menos `--min-measure-s` (60 s),
  e a energia é dividida pelo número de repetições (`measure_repeats`).
* Antes da coleta, o consumo em repouso é medido (`idle_*`).
  `net_energy_J = energy_J − potência_em_repouso × tempo` é a energia
  atribuível ao modelo.

---

# Como executar

## 1. Ambiente

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

## 2. Teste rápido do pipeline (na tomada mesmo)

```bash
python main.py --grid smoke --allow-unmeasured --min-measure-s 5 --idle-s 3 --output output/smoke_test.csv
```

## 3. Coleta na CPU (notebook)

Preparação, para a medição ser comparável entre execuções:

1. Carregue a bateria até 100%.
2. Desative a **Economia de bateria** (ela limita a CPU abaixo de 20%) e deixe o
   modo de energia sempre no mesmo valor (ex.: *Melhor desempenho*).
3. Brilho da tela fixo, Wi-Fi ligado ou desligado sempre do mesmo jeito,
   feche os outros programas (navegador, OneDrive sincronizando etc.).
4. **Desconecte o carregador** e rode:

```bash
python main.py --grid cpu
```

A coleta para sozinha quando a bateria chega a 25% (`--min-battery`) ou se o
carregador for conectado. Para continuar, carregue a bateria e rode o **mesmo
comando** de novo: as configurações já concluídas são puladas.

A grade `cpu` sorteia 48 configurações (~2,5 h no total, ou seja, 2 a 3 cargas
de bateria).

## 4. Coleta na GPU (Colab/Kaggle)

Abra `colab_gpu.ipynb` no Google Colab, escolha o ambiente **GPU T4** e
execute as células. Os resultados vão para o Google Drive
(`MyDrive/ml-energy-estimation/runs_gpu.csv`).

## Opções principais

| Opção               | Padrão            | Descrição                                        |
| ------------------- | ----------------- | ------------------------------------------------ |
| `--grid`            | `smoke`           | `smoke`, `cpu` ou `gpu`                          |
| `--n-configs`       | 48                | quantas combinações sortear da grade             |
| `--repeats`         | 1                 | repetições de cada configuração (variabilidade)  |
| `--min-measure-s`   | 60                | duração mínima de cada janela de medição         |
| `--idle-s`          | 60                | duração da medição em repouso                    |
| `--min-battery`     | 25                | % de bateria em que a coleta para                |
| `--output`          | `output/runs.csv` | arquivo da base de dados                         |

---

# Variáveis dos experimentos (fatores)

| Fator               | Equivalente nos artigos                 | CPU                 | GPU               |
| ------------------- | --------------------------------------- | ------------------- | ----------------- |
| `model`             | arquitetura                             | mlp, lenet5, cnn_small, resnet18 | idem |
| `dataset`           | conjunto de dados                       | mnist, fashion_mnist, cifar10 | idem    |
| `data_fraction`     | tamanho do dataset                      | 0,02 · 0,05 · 0,1   | 0,25 · 0,5 · 1,0  |
| `epochs`            | número de épocas                        | 1 · 2 · 3           | 1 · 2 · 3         |
| `batch_size`        | batch size (Zeus)                       | 32 · 128            | 64 · 256 · 512    |
| `threads`           | paralelismo (análogo a nº de GPUs)      | 2 · 4               | 2                 |
| `inference_samples` | carga de inferência                     | 10k · 50k           | 50k · 200k        |

---

# Colunas da base (`output/runs.csv`)

Cada configuração gera **duas linhas**: `stage = train` e `stage = inference`.
A série temporal de cada execução fica em `output/timeseries/<run_id>_<stage>.csv`.

**Metadados da tarefa** (preditores, como no artigo de regressão simbólica)

| Coluna                  | Descrição                                               |
| ----------------------- | ------------------------------------------------------- |
| `n_params`              | número de parâmetros do modelo                          |
| `flops_per_sample`      | FLOPs de um forward por amostra                         |
| `n_train_samples`       | amostras de treino usadas                               |
| `train_total_flops`     | 3 × FLOPs/amostra × amostras × épocas                   |
| `inference_total_flops` | FLOPs/amostra × amostras de inferência                  |

**Uso de recursos** (média e máximo durante a execução)

| Coluna                         | Descrição                                   |
| ------------------------------ | ------------------------------------------- |
| `execution_time_s`             | tempo de UMA execução (s)                   |
| `avg_cpu_%` / `max_cpu_%`      | uso da CPU (sistema todo)                   |
| `avg_proc_cpu_%`               | uso da CPU só pelo processo do experimento  |
| `avg_ram_%`, `avg_ram_used_GB` | memória RAM do sistema                      |
| `avg_proc_rss_GB`              | RAM usada pelo processo                     |
| `avg_gpu_%`, `avg_vram_%`      | uso da GPU e da memória de vídeo            |

**Energia** (por execução)

| Coluna                   | Descrição                                                   |
| ------------------------ | ----------------------------------------------------------- |
| `energy_J`               | energia **medida** (fonte em `energy_source`)               |
| `net_energy_J`           | energia medida menos o consumo em repouso                   |
| `energy_source`          | `battery_system`, `nvml_gpu` ou `none`                      |
| `battery_energy_J`       | integral da potência da bateria                             |
| `battery_capacity_drop_J`| queda da carga da bateria (conferência, resolução baixa)    |
| `gpu_energy_J`           | energia da GPU (contador do NVML ou integral da potência)   |
| `cpu_energy_est_J`       | **estimativa** linear da CPU                                |
| `ram_energy_est_J`       | **estimativa** da RAM                                       |
| `measure_repeats`        | quantas vezes a etapa foi repetida na janela de medição     |

A energia é integrada pela regra do trapézio usando o horário real de cada
amostra:

$$E = \int P(t)\,dt \approx \sum_i \frac{P_i + P_{i+1}}{2}\,(t_{i+1} - t_i)$$
