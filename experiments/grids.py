"""
Etapa 1 da proposta: definir os experimentos.

Cada fator corresponde a uma variável dos artigos de referência:
arquitetura (model), tamanho do dataset (data_fraction), épocas, batch size
e paralelismo (threads da CPU, análogo à quantidade de GPUs / power limit).

O fatorial completo é grande demais para rodar na bateria, então sorteamos
`n_configs` combinações com semente fixa (reprodutível).
"""
import itertools
import random

# Notebook (CPU, medição pela bateria). Faixas escolhidas para cada execução
# levar de segundos a ~7 min num i7-8565U (o pior caso é resnet18 com 10% e 3 épocas).
CPU_FACTORS = {
    "model": ["mlp", "lenet5", "cnn_small", "resnet18"],
    "dataset": ["mnist", "fashion_mnist", "cifar10"],
    "batch_size": [32, 128],
    "data_fraction": [0.02, 0.05, 0.1],
    "epochs": [1, 2, 3],
    "threads": [2, 4],
    "inference_samples": [10000, 50000],
}

# Colab/Kaggle (GPU T4, medição pelo NVML). A GPU aguenta cargas maiores.
GPU_FACTORS = {
    "model": ["mlp", "lenet5", "cnn_small", "resnet18"],
    "dataset": ["mnist", "fashion_mnist", "cifar10"],
    "batch_size": [64, 256, 512],
    "data_fraction": [0.25, 0.5, 1.0],
    "epochs": [1, 2, 3],
    "threads": [2],
    "inference_samples": [50000, 200000],
}

# Teste rápido do pipeline (poucos segundos por execução)
SMOKE_CONFIGS = [
    {"model": "mlp", "dataset": "mnist", "batch_size": 128, "data_fraction": 0.05,
     "epochs": 1, "threads": 4, "inference_samples": 5000},
    {"model": "lenet5", "dataset": "mnist", "batch_size": 64, "data_fraction": 0.05,
     "epochs": 1, "threads": 2, "inference_samples": 5000},
]


def _sample(factors, n_configs, seed):
    keys = list(factors)
    full = [dict(zip(keys, values)) for values in itertools.product(*factors.values())]
    rng = random.Random(seed)
    # Ordem aleatória também evita que o aquecimento da máquina se correlacione com algum fator
    return rng.sample(full, min(n_configs, len(full)))


def get_grid(name, n_configs=48, seed=42, repeats=1):
    if name == "smoke":
        configs = [dict(c) for c in SMOKE_CONFIGS]
    elif name == "cpu":
        configs = _sample(CPU_FACTORS, n_configs, seed)
    elif name == "gpu":
        configs = _sample(GPU_FACTORS, n_configs, seed)
    else:
        raise ValueError(f"Grade desconhecida: {name}. Opções: smoke, cpu, gpu")

    return [dict(cfg, repeat=r) for r in range(repeats) for cfg in configs]
