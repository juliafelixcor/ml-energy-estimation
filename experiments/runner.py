"""
Etapas 2, 3 e 4 da proposta: executar treino e inferência coletando as
métricas, e organizar tudo numa única base (output/runs.csv).
"""
import hashlib
import json
import math
import os
import platform
import time
from datetime import datetime

import pandas as pd
import torch

from datasets.loaders import get_dataloaders, input_shape
from experiments.features import model_complexity, workload_features
from models import build_model
from monitoring.monitor import SystemMonitor
from stages.inference import run_inference
from stages.train import run_train

CONFIG_KEYS = ["model", "dataset", "batch_size", "data_fraction", "epochs", "threads", "inference_samples", "repeat"]


def run_id(cfg, device):
    key = json.dumps({k: cfg[k] for k in CONFIG_KEYS} | {"device": device}, sort_keys=True)
    return hashlib.md5(key.encode()).hexdigest()[:10]


def _cpu_name():
    try:
        import cpuinfo  # opcional
        return cpuinfo.get_cpu_info()["brand_raw"]
    except Exception:
        return platform.processor()


def _measured_energy(metrics, idle):
    """
    Escolhe a medição REAL disponível como alvo do modelo preditivo:
      - battery_system: notebook fora da tomada (sistema inteiro)
      - nvml_gpu: GPU com sensor de potência (Colab/Kaggle)
    net_energy_J desconta o consumo em repouso (baseline).
    """
    if metrics.get("on_battery") and not math.isnan(metrics.get("battery_energy_J", float("nan"))):
        energy, source, idle_w = metrics["battery_energy_J"], "battery_system", idle.get("idle_battery_power_W")
    elif metrics.get("gpu_energy_J") is not None and not math.isnan(metrics["gpu_energy_J"]):
        energy, source, idle_w = metrics["gpu_energy_J"], "nvml_gpu", idle.get("idle_gpu_power_W")
    else:
        return {"energy_J": float("nan"), "net_energy_J": float("nan"), "energy_source": "none"}

    net = energy - idle_w * metrics["execution_time_s"] if idle_w is not None and not math.isnan(idle_w) else float("nan")
    return {"energy_J": energy, "net_energy_J": net, "energy_source": source}


def _measure_stage(work, min_measure_s, interval, verbose):
    """
    Executa `work()` repetidamente até a janela de medição durar pelo menos
    `min_measure_s`. Medições curtas demais são imprecisas (o sensor da bateria
    atualiza a cada ~5-20 s), então a energia de UMA execução é total / repetições.
    """
    monitor = SystemMonitor(interval, verbose=verbose)
    monitor.start()
    t0 = time.perf_counter()
    repeats = 0
    result = None
    while True:
        result = work()
        repeats += 1
        if time.perf_counter() - t0 >= min_measure_s:
            break
    metrics, ts = monitor.stop()

    metrics["measure_window_s"] = metrics["execution_time_s"]
    metrics["measure_repeats"] = repeats
    # Grandezas extensivas (tempo e energia) passam a ser por execução
    for k in list(metrics):
        if k == "execution_time_s" or k.endswith("_J"):
            metrics[k] = metrics[k] / repeats if metrics[k] is not None else None

    return result, metrics, ts


def run_config(cfg, device, idle, interval=0.5, min_measure_s=60, timeseries_dir="output/timeseries", verbose=True):
    """Executa treino + inferência de uma configuração e retorna as duas linhas da base."""
    rid = run_id(cfg, device)
    torch.set_num_threads(cfg["threads"])
    seed = 1000 + cfg.get("repeat", 0)

    shape = input_shape(cfg["dataset"])
    train_loader, test_loader = get_dataloaders(cfg["dataset"], cfg["batch_size"], cfg["data_fraction"], seed)

    complexity = model_complexity(build_model(cfg["model"], shape), shape)

    base = {
        "run_id": rid,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "host": platform.node(),
        "cpu_name": _cpu_name(),
        "device": device,
        "seed": seed,
        **{k: cfg[k] for k in CONFIG_KEYS},
        **complexity,
        **workload_features(cfg, complexity, len(train_loader.dataset)),
        **idle,
    }

    state = {}

    def train_once():
        torch.manual_seed(seed)
        state["model"] = build_model(cfg["model"], shape)
        return run_train(state["model"], train_loader, cfg["epochs"], device, verbose=False)

    def infer_once():
        return run_inference(state["model"], test_loader, cfg["inference_samples"], device)

    rows = []
    for stage, work in (("train", train_once), ("inference", infer_once)):
        if verbose:
            print(f"   -> {stage}...", end=" ", flush=True)
        if device == "cuda":
            torch.cuda.synchronize()
        acc, metrics, ts = _measure_stage(work, min_measure_s, interval, verbose=False)

        row = {**base, "stage": stage, "accuracy_%": acc, **metrics, **_measured_energy(metrics, idle)}
        rows.append(row)

        if timeseries_dir:
            os.makedirs(timeseries_dir, exist_ok=True)
            ts.to_csv(os.path.join(timeseries_dir, f"{rid}_{stage}.csv"), index=False)

        if verbose:
            print(f"{row['execution_time_s']:.1f}s/exec x{row['measure_repeats']} | "
                  f"energia={row['energy_J']:.1f} J ({row['energy_source']}) | acc={acc:.1f}%")

    return rows


def append_rows(rows, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    df_new = pd.DataFrame(rows)
    if os.path.exists(path):
        df_new = pd.concat([pd.read_csv(path), df_new], ignore_index=True)
    df_new.to_csv(path, index=False)


def completed_run_ids(path):
    if not os.path.exists(path):
        return set()
    df = pd.read_csv(path, usecols=["run_id", "stage"])
    counts = df.groupby("run_id")["stage"].nunique()
    return set(counts[counts == 2].index)
