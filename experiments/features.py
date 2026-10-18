import torch
from torch.utils.flop_counter import FlopCounterMode


def model_complexity(model, in_shape):
    """
    Metadados do modelo usados como variáveis preditoras (como no artigo de
    regressão simbólica): número de parâmetros e FLOPs de um forward por amostra.
    """
    n_params = sum(p.numel() for p in model.parameters())

    model.eval()
    with torch.no_grad(), FlopCounterMode(display=False) as counter:
        model(torch.zeros(1, *in_shape))
    flops = counter.get_total_flops()

    return {"n_params": n_params, "flops_per_sample": flops}


def workload_features(cfg, complexity, n_train_samples):
    """
    Carga de trabalho total de cada etapa. No treino, o backward custa
    aproximadamente 2x o forward, por isso o fator 3.
    """
    return {
        "n_train_samples": n_train_samples,
        "train_total_flops": 3 * complexity["flops_per_sample"] * n_train_samples * cfg["epochs"],
        "inference_total_flops": complexity["flops_per_sample"] * cfg["inference_samples"],
    }
